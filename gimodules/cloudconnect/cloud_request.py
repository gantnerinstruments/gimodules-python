"""
Module to send simplified http request to the Cloud. (Gantner HTTP API for more information)
"""

from __future__ import annotations

from io import BytesIO
import requests
import datetime as dt
import numpy as np
import pandas as pd
import re
import uuid
import time
import logging
import pytz

from dataclasses import dataclass
from typing import List, Dict, Optional, Union, Any, Type, cast, TypedDict, Tuple
from requests.auth import HTTPBasicAuth
from enum import Enum
from dateutil import tz

from gimodules.cloudconnect import utils, authenticate

# Set output level to INFO because default is WARNNG
logging.getLogger().setLevel(logging.INFO)


@dataclass
class CsvConfig:
    """Object for tracking parameters for csv import"""

    ColumnSeparator: str = ";"
    DecimalSeparator: str = ","
    NameRowIndex: int = 0
    UnitRowIndex: int = 0
    ValuesStartRowIndex: int = 1
    ValuesStartColumnIndex: int = 1
    # Column 1: Date and Time -> specified in Gantner http docs
    # Comment one out: if python formatter differs from C++ formatter
    # "%d.%m.%Y %H:%M:%S.%F" on backend -> "%d.%m.%Y %H:%M:%S.%f" for python
    DateTimeFmtColumn1: str = "%d.%m.%Y %H:%M:%S.%F"
    DateTimeFmtColumn2: str = ""
    DateTimeFmtColumn3: str = ""

    def get_config(self):
        """returns config as dict"""
        return {
            "ColumnSeparator": self.ColumnSeparator,
            "DecimalSeparator": self.DecimalSeparator,
            "NameRowIndex": self.NameRowIndex,
            "UnitRowIndex": self.UnitRowIndex,
            "ValuesStartRowIndex": self.ValuesStartRowIndex,
            "ValuesStartColumnIndex": self.ValuesStartColumnIndex,
            "DateTimeFmtColumn1": self.DateTimeFmtColumn1,
            "DateTimeFmtColumn2": self.DateTimeFmtColumn2,
            "DateTimeFmtColumn3": self.DateTimeFmtColumn3,
        }


@dataclass()
class GIStream:
    """Object for tracking available streams"""

    name: str
    id: str
    sample_rate_hz: str
    first_ts: int
    last_ts: int
    index: int


@dataclass()
class GIStreamVariable:
    """Object for tracking available variables"""

    id: str
    name: str
    index: str
    unit: str
    data_type: str
    sid: str


class Helpers:
    @staticmethod
    def remove_hex_from_string(str):
        """Remove hex value from input string"""
        return re.sub(r"[^\x00-\x7f]", r"", str)


class Resolution(Enum):
    MONTH = "MONTH"
    WEEK = "WEEK"
    DAY = "DAY"
    HOUR = "HOUR"
    QUARTER_HOUR = "QUARTER_HOUR"
    MINUTE = "MINUTE"
    SECOND = "SECOND"
    HZ10 = "HZ10"
    HZ100 = "HZ100"
    KHZ = "KHZ"
    KHZ10 = "KHZ10"
    NANOS = "nanos"


class DataFormat(Enum):
    COL = "col"
    ROW = "row"
    JSON = "json"
    CSV = "csv"
    UDBF = "udbf"
    FAMOS = "famos"
    MDF = "mdf"
    MAT = "mat"


class DataType(Enum):
    EQUIDISTANT = "equidistant"
    ABSOLUTE = "absolute"
    AUTO = "auto"
    FFT = "fft"


class Variable(TypedDict):
    SID: str
    VID: str
    Selector: str


class CSVSettings(TypedDict, total=False):
    HeaderText: str
    AddColumnHeader: bool
    DateTimeHeader: str
    DateTimeFormat: str
    ColumnSeparator: str
    DecimalSeparator: str


class LogSettings(TypedDict, total=False):
    SourceID: str
    SourceName: str
    MeasurementName: str


def get_sample_rate(resolution: str):
    if resolution == "MONTH":
        return 1 / (30 * 24 * 60 * 60)
    elif resolution == "WEEK":
        return 1 / (7 * 24 * 60 * 60)
    elif resolution == "DAY":
        return 1 / (24 * 60 * 60)
    elif resolution == "HOUR":
        return 1 / (60 * 60)
    elif resolution == "QUARTER_HOUR":
        return 1 / (15 * 60)
    elif resolution == "MINUTE":
        return 1 / 60
    elif resolution == "SECOND":
        return 1
    elif resolution == "HZ10":
        return 10
    elif resolution == "HZ100":
        return 100
    elif resolution == "KHZ":
        return 1_000
    elif resolution == "KHZ10":
        return 10_000
    elif resolution == "nanos":
        return 1 / 1e9
    else:
        return 1


class CloudRequest:
    def __init__(self) -> None:
        self.url: str | None = ""
        self.user: str = ""
        self.pw: str = ""
        self.login_token: Optional[Dict[str, str | None]] = None
        self.refresh_token: Optional[str] = None
        self.streams: dict[str, GIStream] | None = None
        self.stream_variabels: dict[str, GIStreamVariable] | None = None
        self.query: str = ""
        self.request_measurement_res = None
        self.timezone: str = "Europe/Vienna"

        # Enums
        self.resolutions = Resolution
        self.units: Type[Any] = cast(Type[Enum], Enum("Units", {}))

        # Importer data
        self.import_session_res_udbf = None
        self.import_session_res_csv = None
        self.import_session_csv_current: dict | None = None
        self.session_ID = None
        self.csv_config = CsvConfig()

    def login(
        self,
        access_token: Optional[str] = None,
        url: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        use_env_file: bool = False,
    ) -> None:
        """Login method that handles Bearer Token/tenant,
        username/password logins, or .env file.
        .env file should look like:

        CLOUD_TENANT='https://demo.gi-cloud.io'
        BEARER_TOKEN=''

        """

        if url and access_token:
            self.login_token = {"access_token": access_token}
            self.url = url
        elif url and user and password:
            self.url = url
            self.user = user
            self.pw = password
        elif use_env_file:
            tenant, bearer_token, refresh_token = authenticate.load_env_variables()
            logging.info(bearer_token)
            self.url = tenant
            self.login_token = {
                "access_token": bearer_token,
                "refresh_token": refresh_token,
            }
        else:
            raise ValueError("Invalid arguments provided for login")

        if user and password:
            login_form = {
                "username": self.user,
                "password": self.pw,
                "grant_type": "password",
            }
            auth = HTTPBasicAuth("gibench", "")
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            login_url = f"{self.url}/token"

            try:
                res = requests.post(login_url, data=login_form, headers=headers, auth=auth)
                if res.status_code == 200:
                    self.login_token = res.json()
                    self.refresh_token = (
                        (self.login_token.get("refresh_token")) if self.login_token else None
                    )
                    logging.info("Login successful")
                else:
                    logging.error(
                        f"Login failed! Response Code:" f" {res.status_code}, Reason: {res.reason}"
                    )
            except requests.RequestException as e:
                logging.warning(f"Request error during login: {e}")

        try:
            assert self.login_token, "Login token is None even after Login!!"
            # Set headers for future requests after login
            self.headers: dict = {"Authorization": f"Bearer {self.login_token['access_token']}"}
            self.get_all_stream_metadata()
            self.print_streams()
            self.get_all_var_metadata()
        except Exception as e:
            logging.error(f"Login post-processing failed: {e}")
            raise Exception(f"Login failed! {e}")

    def refresh_access_token(self) -> None:
        """
        Refresh the access token with a refresh token.
        The refresh token is valid for 14 days.
        """
        if not self.refresh_token:
            logging.error("No refresh token available for refreshing access token.")
            return

        # Prepare request
        refresh_form = {
            "ClientID": "gibench",
            "RefreshToken": self.refresh_token,
        }
        headers = {"Content-Type": "application/json"}
        refresh_url = f"{self.url}/rpc/AdminAPI.RefreshToken"

        # Send request
        try:
            res = requests.post(refresh_url, json=refresh_form, headers=headers)
            if res.status_code == 200:
                response_data = res.json()
                self.login_token = {
                    "access_token": response_data.get("AccessToken"),
                    "refresh_token": response_data.get("RefreshToken", self.refresh_token),
                }
                logging.info("Access token refreshed successfully.")
            else:
                logging.error(
                    f"Failed to refresh access token. Response Code: "
                    f"{res.status_code}, Reason: {res.reason}"
                )
        except requests.RequestException as e:
            logging.warning(f"Request error while refreshing access token: {e}")

    from typing import Optional, Dict

    def get_all_stream_metadata(self) -> Dict[Any, GIStream]:
        """
        Loads the available meta information from all available streams.
        The data is stored in data classes (GIStream)
        and is accessible via the .streams attribute.

        Returns:
            A dictionary of stream metadata if successful, otherwise None.
        """
        if not self.login_token:
            logging.error("You have no valid access token! Please login first.")
            return None

        # Prepare request
        url_list = f"{self.url}/kafka/structure/sources"
        # Send request
        try:
            res = requests.get(url_list, headers=self.headers)
            if res.status_code == 200:
                response_data = res.json()
                self.streams = {}  # Reset memory
                for stream in response_data["Data"]:
                    name = stream["Name"]
                    stream_id = stream["Id"]
                    sample_rate_hz = stream["SampleRateHz"]
                    first_ts = stream["AbsoluteStart"]
                    last_ts = stream["LastTimeStamp"]
                    index = stream["Index"]
                    # Store data in dict with dataclass
                    self.streams[stream_id] = GIStream(
                        name,
                        stream_id,
                        sample_rate_hz,
                        first_ts,
                        last_ts,
                        index,
                    )
                return self.streams
            elif res.status_code in {401, 403}:
                self.refresh_access_token()
                res = requests.get(url_list, headers=self.headers)
                if res.status_code == 200:
                    return self.get_all_stream_metadata()
                else:
                    logging.error(f"Failed after token refresh! Code: {res.status_code}")
            else:
                logging.error(f"Failed! Code: {res.status_code}, Reason: {res.reason}")
        except requests.RequestException as e:
            logging.warning(f"Request error while fetching stream metadata: {e}")

        return None

    def print_streams(self) -> None:
        """
        Prints the available streams' metadata.
        """
        if not self.streams:
            logging.info("You have no loaded streams.")
            return

        for stream in self.streams.values():
            first_ts_str = dt.datetime.utcfromtimestamp(float(stream.first_ts) / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            last_ts_str = dt.datetime.utcfromtimestamp(float(stream.last_ts) / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            logging.info(
                f"{'Streamname:':<20}{stream.name}\n"
                f"{'Streamid:':<20}{stream.id}\n"
                f"{'first ts:':<20}{stream.first_ts} {first_ts_str}\n"
                f"{'last ts:':<20}{stream.last_ts} {last_ts_str}\n"
                f"{'Samplerate:':<20}{stream.sample_rate_hz}\n"
            )

    def get_all_var_metadata(self) -> None:
        """
        Loads the available meta information from all available variables.
        The data is stored in data classes
        and is accessible via the .stream_variabels attribute.
        """
        if not self.streams:
            logging.info("You have no loaded streams. Please load streams first.")
            return

        # Prepare request
        url_list = f"{self.url}/__api__/gql"
        assert self.login_token, "No valid access token. Please log in first."
        headers = {"Authorization": f"Bearer {self.login_token['access_token']}"}
        self.stream_variabels = {}  # Reset memory
        unit_names = set()  # Use a set to avoid duplicate units

        for stream in self.streams.values():
            query = f"""
            {{
                variableMapping(sid: "{stream.id}") {{
                    sid
                    columns {{
                        name
                        variables {{
                            id
                            dataType
                            name
                            unit
                        }}
                    }}
                }}
            }}
            """

            try:
                res = requests.post(url_list, json={"query": query}, headers=headers)

                if res.status_code == 200:
                    response_data = res.json()
                    if not isinstance(response_data, dict):
                        logging.error("Response data is not a dictionary!")
                        return
                    columns = (
                            response_data.get("data", {})
                            .get("variableMapping", {}) or {}
                    ).get("columns")
                    if not columns: # Skip if stream has no mapping
                        logging.info(f"No variable mapping available for stream {stream.name}"
                                     f" with sid {stream.id}.")
                        continue
                    #columns = response_data["data"]["variableMapping"]["columns"]
                    sid = response_data["data"]["variableMapping"]["sid"]

                    for column in columns:
                        index = column["name"]  # Var index in GI System
                        variable = column["variables"][0]  # Assuming there's always one variable
                        name = variable["name"]
                        data_type = variable["dataType"]
                        variable_id = variable["id"]
                        unit = variable["unit"]

                        # Add unit to set if not empty
                        if unit:
                            unit_names.add(unit)

                        # Create unique variable name
                        self.stream_variabels[f"{stream.name}__{name}"] = GIStreamVariable(
                            variable_id, name, index, unit, data_type, sid
                        )
                elif res.status_code in {401, 403}:
                    self.refresh_access_token()
                    # Retry once after refreshing the token
                    res = requests.post(url_list, json={"query": query}, headers=headers)
                    if res.status_code != 200:
                        logging.error(
                            f"Fetching variable info failed after token refresh!"
                            f" Code: {res.status_code}"
                        )
                else:
                    logging.error(
                        f"Fetching variable info failed! "
                        f"Code: {res.status_code}, Reason: {res.reason}"
                    )
            except requests.RequestException as e:
                logging.warning(f"Request error while fetching variable metadata: {e}")

        # Create Enum for available units
        self.units = cast(Type[Enum], Enum("Units", {unit: unit for unit in unit_names}))

    def variable_info(self) -> Any | None:
        """
        Use this endpoint to read information for all available online variables.

        Returns:
            The parsed JSON response if successful, otherwise None.
        """
        if not self.login_token:
            logging.error("No valid access token. Please log in first.")
            return None

        # Prepare request
        url_list = f"{self.url}/online/structure/variables"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.login_token['access_token']}",
        }

        # Send request
        try:
            res = requests.get(url_list, headers=headers)
            if res.status_code == 200:
                response_data = res.json()
                # TODO: Implement processing of response_data here if needed
                return response_data
            else:
                logging.error(
                    f"Fetching variable info failed!"
                    f" Response Code: {res.status_code}, Reason: {res.reason}"
                )
        except requests.RequestException as e:
            logging.warning(f"Request error while fetching variable info: {e}")

        return None

    def find_var(self, var_name: Union[str, list[str]]) -> Dict[str, GIStreamVariable] | None:
        """
        Searches the existing variables.

        Args:
            var_name (Union[str, list[str]]): Variable name or a list of substrings.

        Returns:
            Optional[Dict[str, GIStreamVariable]]: Dictionary of found variables
            or None if no matches.
        """
        if not self.stream_variabels:
            logging.info("No variables are available to search.")
            return None

        # Search logic
        if isinstance(var_name, list):
            var_name_set = set(var_name)  # Use set for faster lookup
            match = [k for k in self.stream_variabels.keys() if any(vr in k for vr in var_name_set)]
        else:
            match = [k for k in self.stream_variabels.keys() if var_name in k]

        if not match:
            logging.info("No variable found.")
            return None

        # Create the result dictionary for matching variables
        result = {m: self.stream_variabels[m] for m in match}
        return result

    def filter_var_attr(self, attr: str, value: str) -> List[GIStreamVariable] | None:
        """
        Search for stream_variables with a certain attribute.

        Args:
            attr (str): The attribute to filter by (e.g., "unit").
            value (str): The value to match for the specified attribute (e.g., "C°").

        Returns:
            Optional[List[GIStreamVariable]]: A list of matching variables,
             or None if no matches found.
        """
        if not self.stream_variabels:
            logging.info("No stream variables available to filter.")
            return None

        # Filtering based on the attribute and value
        match = [var for var in self.stream_variabels.values() if getattr(var, attr, "") == value]

        return match if match else None

    @staticmethod
    def _build_sensorid_querystring(
        indices: List[str], aggregations: List[str] | None = None
    ) -> str:
        """
        Builds a query string for the sensor IDs with optional aggregations.

        Args:
            indices (List[str]): A list of sensor indices.
            aggregations (Optional[List[str]]): A list of aggregations to apply.
            Defaults to ["avg"] if not provided.

        Returns:
            str: The constructed query string.
        """
        # Default aggregation to "avg" if none are provided
        if not aggregations:
            aggregations = ["avg"]

        # Create the aggregation string
        agg_str = " ".join(aggregations)

        # Build the query string for each index
        query_parts = [
            f"""
            {i} {{
                {agg_str}
            }}
            """
            for i in indices
        ]

        return "\n".join(query_parts)

    def get_var_data_batched(
        self,
        sid: str,
        index_list: List,
        start_date: str,
        end_date: str,
        resolution: str = "nanos",
        custom_column_names: List | None = None,
        timezone: str = "UTC",
        max_points: int = 700_000,
    ):
        """BETA: This makes batched calls to GraphQL. Not recommended.
        This is still about 2x slower than get_data_as_csv() since we make more http requests"""
        if custom_column_names is None:
            custom_column_names = []
        tss, tse = map(self.convert_datetime_to_unix, [start_date, end_date])
        duration_seconds = (tse - tss) // 1000
        sample_rate = get_sample_rate(resolution)
        total_points = sample_rate * len(index_list) * duration_seconds

        if total_points > max_points:
            num_batches = (total_points // max_points) + 1
            timestamps = np.linspace(tss, tse, num_batches + 1, dtype=int)
            logging.info(f"Total points: {total_points}, Num batches: {num_batches}")
            return pd.concat(
                [
                    self.get_var_data_batch(
                        sid,
                        index_list,
                        timestamps[i],
                        timestamps[i + 1],
                        resolution,
                        custom_column_names,
                        timezone,
                    )
                    for i in range(num_batches)
                ]
            ).reset_index(drop=True)
        return self.get_var_data_batch(
            sid, index_list, tss, tse, resolution, custom_column_names, timezone
        )

    def get_var_data_batch(
        self, sid, index_list, tss, tse, resolution, custom_column_names, timezone
    ):
        selected_index_string = (
            ",".join([f'"{index}"' for index in index_list]) if index_list else ""
        )
        if not selected_index_string:
            logging.info("No variable selected")
            return None

        query = f"""
                {{
                    analytics(
                        from: {tss},
                        to: {tse},
                        resolution: {resolution},
                        sid: "{sid}"
                    ) {{
                        ts
                        {self._build_sensorid_querystring(index_list)}
                    }}
                }}
            """

        res = self._execute_gql_request(query)
        if not res:
            return None

        requested_data = res.json()
        if resolution == "nanos":
            data_matrix = requested_data["data"]["Raw"]["data"]
        else:
            data_matrix = np.column_stack(
                (
                    [requested_data["data"]["analytics"]["ts"]]
                    + [requested_data["data"]["analytics"][idx]["avg"] for idx in index_list]
                )
            )

        data_matrix = np.array(data_matrix, dtype=float)
        valid_data = data_matrix[~np.isnan(data_matrix).any(axis=1)]

        columns = (
            custom_column_names if custom_column_names else self.__get_column_names(sid, index_list)
        )
        df = pd.DataFrame(valid_data, columns=columns)
        df["Time"] = pd.to_datetime(df["Time"], unit="ms")
        self.__convert_df_time_from_utc_to_tz(df, timezone)
        return df

    def _execute_gql_request(self, query):
        url = f"{self.url}/__api__/gql"
        headers = {"Authorization": f"Bearer {self.login_token['access_token']}"}
        res = requests.post(url, json={"query": query}, headers=headers)

        if res.status_code == 200 and "errors" not in res.text:
            return res
        elif res.status_code in [401, 403]:
            logging.info("Token expired. Renewing...")
            self.refresh_access_token()
            return self._execute_gql_request(query)
        logging.error(f"Request failed with code {res.status_code}: {res.text}")
        return None

    def get_var_data(
        self,
        sid: str,
        index_list: List[str],
        start_date: str,
        end_date: str,
        resolution: str = "nanos",
        custom_column_names: List[str] | None = None,
        timezone: str = "UTC",
    ) -> pd.DataFrame | None:
        """
        Returns a pandas DataFrame with timestamps and values directly from a data stream.

        Args:
            sid (str): Stream ID.
            index_list (List[str]): List of channel indices (e.g., ["a10", "a11"]).
            start_date (str): Start date in format "YYYY-MM-DD HH:MM:SS".
            end_date (str): End date in format "YYYY-MM-DD HH:MM:SS".
            resolution (str, optional): Data resolution. Defaults to "nanos".
            custom_column_names (Optional[List[str]], optional):
            Custom column names for the DataFrame.
            timezone (str, optional): Timezone for the data. Defaults to "UTC".

        Returns:
            Optional[pd.DataFrame]: DataFrame containing the requested data,
            or None if the request failed.
        """
        tss = str(self.convert_datetime_to_unix(start_date))
        tse = str(self.convert_datetime_to_unix(end_date))

        # Build the query
        if resolution == "nanos" and index_list:
            selected_index_string = ", ".join(f'"{idx}"' for idx in index_list)
            self.query = f"""
            {{
                Raw(columns: ["ts", "nanos", {selected_index_string}],
                sid: "{sid}",
                from: {tss},
                to: {tse}) {{
                    data
                }}
            }}
            """
        elif index_list:
            selected_index_string = self._build_sensorid_querystring(index_list)
            self.query = f"""
            {{
                analytics(
                    from: {tss},
                    to: {tse},
                    resolution: {resolution},
                    sid: "{sid}"
                ) {{
                    ts
                    {selected_index_string}
                }}
            }}
            """
        else:
            logging.info("No variable selected")
            return None

        # Send the request
        url_list = f"{self.url}/__api__/gql"
        try:
            res = requests.post(url_list, json={"query": self.query}, headers=self.headers)
            if res.status_code == 200 and "errors" not in res.text:
                requested_data = res.json()

                # Filter data out of the request
                if resolution == "nanos":
                    data_matrix = requested_data["data"]["Raw"]["data"]
                    self.data = np.array(data_matrix, dtype=float)
                else:
                    self.data = np.zeros(
                        (
                            len(requested_data["data"]["analytics"]["ts"]),
                            len(index_list) + 1,
                        )
                    )
                    self.data[:, 0] = requested_data["data"]["analytics"]["ts"]
                    for k, idx in enumerate(index_list):
                        self.data[:, k + 1] = requested_data["data"]["analytics"][idx]["avg"]

                # Clean the data by removing leading/trailing NaNs
                valid_rows = ~np.isnan(self.data).any(axis=1)
                self.data = self.data[valid_rows]

                # Create the DataFrame
                column_names = custom_column_names or self.__get_column_names(sid, index_list)
                self.df = pd.DataFrame(self.data, columns=column_names)

                # Convert time column to datetime and adjust timezone
                self.df["Time"] = pd.to_datetime(self.df["Time"], unit="ms")
                self.__convert_df_time_from_utc_to_tz(timezone)

                return self.df
            elif res.status_code in {401, 403}:
                logging.info("Token expired. Renewing...")
                self.refresh_access_token()
                # Retry once after refreshing the token
                return self.get_var_data(
                    sid,
                    index_list,
                    start_date,
                    end_date,
                    resolution,
                    custom_column_names,
                    timezone,
                )
            else:
                error = res.json().get("errors", [{}])[0].get("message", "Unknown error")
                logging.error(
                    f"Fetching data failed!"
                    f"Response Code: {res.status_code}, Reason: {res.reason}, Msg: {error}"
                )
        except requests.RequestException as e:
            logging.warning(f"Request error while fetching variable data: {e}")

        return None

    def get_data_np(
        self,
        sid: str,
        index_list: List[str],
        tss: str,
        tse: str,
        resolution: str = "nanos",
    ) -> np.ndarray | None:
        """
        Returns a numpy matrix of data with timestamps and values directly from a data stream.

        Args:
            sid (str): Stream ID.
            index_list (List[str]): List of channel indices (e.g., ["a10", "a11"]).
            tss (str): Start timestamp.
            tse (str): End timestamp.
            resolution (str, optional): Data resolution. Defaults to "nanos".

        Returns:
            Optional[np.ndarray]: Numpy matrix containing the requested data,
             or None if the request failed.
        """
        if not index_list:
            logging.info("No variable selected.")
            return None

        # Build the query
        if resolution == "nanos":
            selected_index_string = ", ".join(f'"{idx}"' for idx in index_list)
            self.query = f"""
            {{
                Raw(columns: ["ts", "nanos", {selected_index_string}],
                sid: "{sid}",
                from: {tss},
                to: {tse}) {{
                    data
                }}
            }}
            """
        else:
            selected_index_string = self._build_sensorid_querystring(index_list)
            self.query = f"""
            {{
                analytics(
                    from: {tss},
                    to: {tse},
                    resolution: {resolution},
                    sid: "{sid}"
                ) {{
                    ts
                    {selected_index_string}
                }}
            }}
            """

        # Send the request
        url_list = f"{self.url}/__api__/gql"
        try:
            res = requests.post(url_list, json={"query": self.query}, headers=self.headers)
            if res.status_code == 200 and "errors" not in res.text:
                requested_data = res.json()

                # Filter data out of the request
                if resolution == "nanos":
                    data_matrix = requested_data["data"]["Raw"]["data"]
                    self.data = np.array(data_matrix, dtype=float)
                else:
                    ts_data = requested_data["data"]["analytics"]["ts"]
                    self.data = np.zeros((len(ts_data), len(index_list) + 1), dtype=float)
                    self.data[:, 0] = ts_data
                    for k, idx in enumerate(index_list):
                        self.data[:, k + 1] = requested_data["data"]["analytics"][idx]["avg"]

                # Clean the data by removing leading/trailing NaNs
                valid_rows = ~np.isnan(self.data).any(axis=1)
                self.data = self.data[valid_rows]

                return self.data
            elif res.status_code in {401, 403}:
                logging.info("Token expired. Renewing...")
                self.refresh_access_token()
                # Retry once after refreshing the token
                return self.get_data_np(sid, index_list, tss, tse, resolution)
            else:
                error = res.json().get("errors", [{}])[0].get("message", "Unknown error")
                logging.error(
                    f"Fetching data failed!"
                    f" Response Code: {res.status_code}, Reason: {res.reason}, Msg: {error}"
                )
        except requests.RequestException as e:
            logging.warning(f"Request error while fetching data: {e}")

        return None

    def _get_stream_name_for_sid_vid(self, sid: str, vid: str) -> str | None:
        """
        Retrieves the stream name for a given stream ID (sid) and variable ID (vid).

        Args:
            sid (str): Stream ID.
            vid (str): Variable ID.

        Returns:
            Optional[str]: The stream name if found, otherwise None.
        """
        if self.stream_variabels is not None:
            stream = [k for k, v in self.stream_variabels.items() if v.sid == sid and v.id == vid]
            if len(stream) == 1:
                return stream[0].split("__")[0]

        logging.info("No stream variables available or matching stream not found.")
        return None

    def _get_stream_name_for_sid(self, sid: str) -> str | None:
        """
        Retrieves the stream name for a given stream ID (sid).

        Args:
            sid (str): Stream ID.

        Returns:
            Optional[str]: The stream name if found, otherwise None.
        """
        if self.stream_variabels is not None and self.streams is not None:
            stream = [
                gi_stream.name
                for gi_stream in self.streams.values()
                if gi_stream.id == sid
            ]
            if len(stream) == 1:
                return stream[0]

        logging.info("No stream variables available or matching stream not found.")
        return None

    def get_all_vars_of_stream(self, sid: str) -> List[GIStreamVariable]:
        """
        Retrieves all variables associated with a given stream ID (sid).

        Args:
            sid (str): Stream ID.

        Returns:
            List[GIStreamVariable]: A list of variables for the given stream ID.
        """
        if self.stream_variabels is not None:
            return [v for v in self.stream_variabels.values() if v.sid == sid]

        logging.info("No stream variables available.")
        return []

    def get_data_as_csv(
        self,
        variables: List[GIStreamVariable],
        resolution: str,
        start: str,
        end: str,
        filepath: str = "",
        streaming: bool = True,
        return_df: bool = True,
        write_file: bool = True,
        decimal_sep: str = ".",
        delimiter: str = ";",
        timezone: str = "UTC",
        aggregation: str = "avg",
    ) -> pd.DataFrame | None:
        """
        Returns a CSV file with the data of a given list of variables.

        Args:
            variables (List[GIStreamVariable]): List of variables to include in the export.
            resolution (str): Data resolution.
            start (str): Start date in "YYYY-MM-DD HH:MM:SS" format.
            end (str): End date in "YYYY-MM-DD HH:MM:SS" format.
            filepath (str, optional): Path to save the file. Defaults to "".
            streaming (bool, optional): Whether to stream the response. Defaults to True.
            return_df (bool, optional): Whether to return a DataFrame. Defaults to True.
            write_file (bool, optional): Whether to write the file to disk. Defaults to True.
            decimal_sep (str, optional): Decimal separator for the CSV. Defaults to ".".
            delimiter (str, optional): Field delimiter for the CSV. Defaults to ";".
            timezone (str, optional): Timezone for the export. Defaults to "UTC".
            aggregation (str, optional): Aggregation type. Defaults to "avg".

        Returns:
            Optional[pd.DataFrame]: The data as a pandas DataFrame if return_df is True,
            otherwise None.
        """
        # Build query and filename
        substring = ""
        streams = set()
        for var in variables:
            stream = self._get_stream_name_for_sid_vid(var.sid, var.id)
            streams.add(stream)
            substring += f"""{{
                field: "{var.sid}:{var.index}.{aggregation}",
                headers: ["{var.name}", "{stream}", "{aggregation}", "{var.unit or ''}"]
            }},"""

        filename = f"{'_'.join(filter(None, streams))}_{start}_{end}_{resolution}_{aggregation}.csv"
        start_unix = str(self.convert_datetime_to_unix(start))
        end_unix = str(self.convert_datetime_to_unix(end))
        self.query = f"""
        {{
            exportCSV(
                resolution: {resolution}
                from: {start_unix},
                to: {end_unix},
                timezone: "{timezone}",
                filename: "{filename}"
                columns: [
                    {{
                        field: "ts",
                        headers: ["datetime"],
                        dateFormat: "%Y-%m-%dT%H:%M:%S"
                    }},
                    {{
                        field: "ts",
                        headers: ["time", "", "", "[s since 01.01.1970]"]
                    }},
                    {substring}
                ]
            ) {{
                file
            }}
        }}
        """
        # Send request
        url_list = f"{self.url}/__api__/gql"
        try:
            res = requests.post(
                url_list,
                json={"query": self.query},
                headers=self.headers,
                stream=streaming,
            )
            if res.status_code == 200 and "errors" not in res.text:
                if write_file:
                    with open(f"{filepath}{filename}", "wb") as csv_file:
                        if not streaming:
                            csv_file.write(res.content)
                        else:
                            for chunk in res.iter_content(chunk_size=1024):
                                csv_file.write(chunk)
                                csv_file.flush()
                        if not return_df:
                            return None

                # Return as DataFrame
                if return_df:
                    if not streaming or not write_file:
                        return pd.read_csv(
                            BytesIO(res.content),
                            delimiter=delimiter,
                            decimal=decimal_sep,
                        )
                    else:
                        return pd.read_csv(
                            f"{filepath}{filename}",
                            delimiter=delimiter,
                            decimal=decimal_sep,
                        )
            else:
                error_message = res.json().get("errors", [{}])[0].get("message", "Unknown error")
                logging.error(
                    f"Fetching CSV data failed!"
                    f" Response Code: {res.status_code}, Reason: {res.reason}, Msg: {error_message}"
                )
        except requests.RequestException as e:
            logging.warning(f"Request error while fetching CSV data: {e}")

        return None

    def __get_column_names(self, sid: str, index_list: List[str]) -> List[str]:
        """
        Private helper method to get the column names for the DataFrame.

        Args:
            sid (str): Stream ID.
            index_list (List[str]): List of variable indices (e.g., ["a10"]).

        Returns:
            List[str]: List of column names for the DataFrame.
        """
        col_names = ["Time"]
        res = self.filter_var_attr("sid", sid)
        if res is not None:
            for i in index_list:
                for x in res:
                    if x.index == i:
                        col_names.append(x.name)
        return col_names

    @staticmethod
    def convert_datetime_to_unix(datetime_str: str) -> float | None:
        """
        Converts a datetime string to a Unix timestamp in milliseconds.

        Args:
            datetime_str (str): The datetime string in "YYYY-MM-DD HH:MM:SS" format.

        Returns:
            Optional[float]: The Unix timestamp in milliseconds, or None if conversion fails.
        """
        try:
            date_time_obj = dt.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            timestamp_utc = date_time_obj.replace(tzinfo=tz.gettz("UTC"))
            timestamp = int(dt.datetime.timestamp(timestamp_utc)) * 1000
            return timestamp
        except ValueError as err:
            logging.error(f"Error converting '{datetime_str}' to Unix timestamp: {err}")
            return None

    def set_timezone(self, timezone: str = "Europe/Vienna") -> None:
        """
        Sets the timezone if it is valid.

        Args:
            timezone (str): The timezone to set. Defaults to "Europe/Vienna".
        """
        if self.__validate_timezone(timezone):
            self.timezone = timezone
            logging.info(f"Timezone set to: {timezone}")
        else:
            logging.warning(f"Invalid timezone: {timezone}")

    @staticmethod
    def __validate_timezone(timezone: str) -> bool:
        """
        Validates if the given timezone is recognized.

        Args:
            timezone (str): The timezone string to validate.

        Returns:
            bool: True if the timezone is valid, False otherwise.
        """
        try:
            pytz.timezone(timezone)
            return True
        except pytz.UnknownTimeZoneError:
            return False

    def __convert_df_time_from_utc_to_tz(self, df: pd.DataFrame, timezone: str = "UTC") -> None:
        """
        Converts the timestamps of the DataFrame to the desired time zone.

        Args:
            timezone (str): The target time zone. Defaults to "UTC".

        The data is initially in UTC, and the default conversion is to 'UTC'.
        """
        try:
            df["Time"] = df["Time"].dt.tz_localize("UTC")
            df["Time"] = df["Time"].dt.tz_convert(timezone)
        except (AttributeError, TypeError) as err:
            logging.error(f"Error converting DataFrame time to timezone '{timezone}': {err}")

    def get_measurement_limit(
        self,
        sid: str,
        limit: int,
        start_ts: int = 0,
        end_ts: int = 9999999999999,
        sort: str = "DESC",
    ) -> dict | None:
        """
        Retrieves measurement periods for a given stream ID (sid) with a specified limit.
        Timestamps cannot be floats!

        Args:
            sid (str): Stream ID.
            limit (int): The maximum number of measurement periods to retrieve.
            start_ts (int, optional): The start timestamp. Defaults to 0.
            end_ts (int, optional): The end timestamp. Defaults to 9999999999999.
            sort (str, optional): The sort order. Defaults to 'DESC'.

        Returns:
            Optional[dict]: The response JSON if the request is successful, otherwise None.
        """
        query_measurement = f"""
        {{
            measurementPeriods(
                sid: "{sid}",
                from: {start_ts},
                to: {end_ts},
                limit: {limit},
                sort: {sort}
            ) {{
                minTs
                maxTs
                mid
                sampleRate
            }}
        }}
        """
        url_list = f"{self.url}/__api__/gql"

        try:
            res = requests.post(url_list, json={"query": query_measurement}, headers=self.headers)
            if res.status_code == 200:
                self.request_measurement_res = res.json()
                return self.request_measurement_res
            else:
                logging.error(
                    f"Fetching measurement info failed!"
                    f" Response Code: {res.status_code}, Reason: {res.reason}"
                )
        except requests.RequestException as err:
            logging.warning(f"Request error while fetching measurement info: {err}")

        return None

    def print_measurement(self) -> np.ndarray | None:
        """
        Retrieves a list of measurement periods with their start and stop timestamps.

        Returns:
            Optional[np.ndarray]: A NumPy array with start and stop timestamps,
             or None if data is unavailable.
        """
        if not self.request_measurement_res or "data" not in self.request_measurement_res:
            logging.warning("Measurement data is not available.")
            return None

        periods = self.request_measurement_res["data"].get("measurementPeriods", [])
        limit = len(periods)
        measurement_list = np.zeros((limit, 2))

        for measurement_i in range(limit):
            measurement_list[measurement_i, 0] = periods[measurement_i]["minTs"]
            measurement_list[measurement_i, 1] = periods[measurement_i]["maxTs"]

        return measurement_list

    # ubdf importer
    def _create_import_session_udbf(self, sid: str, stream_name: str) -> Union[dict, str] | None:
        """
        Creates an import session for a UDBF file using the HTTP API.

        Args:
            sid (str): The source ID for the data import.
            stream_name (str): The name of the data stream.

        Returns:
            Optional[Union[dict, str]]: The response JSON if the request is successful,
            otherwise None.
        """
        url_list = f"{self.url}/history/data/import"
        param = {
            "Type": "udbf",
            "SourceID": sid,
            "SourceName": stream_name,
            "MeasID": "",
            "SessionTimeoutSec": "300",
            "AddTimeSeries": "false",
            "SampleRate": "-1",
            "AutoCreateMetaData": "true",
        }
        try:
            res = requests.post(url_list, headers=self.headers, json=param)
            if res.status_code == 200:
                self.import_session_res_udbf = res.json()
                logging.info(
                    f"Import session created for UDBF file: {self.import_session_res_udbf}"
                )
                return self.import_session_res_udbf
            else:
                logging.error(
                    f"Creating import session failed!"
                    f" Response Code: {res.status_code}, Reason: {res.reason}"
                )
        except requests.RequestException as err:
            logging.error(f"Failed to create import session: {err}")

        return None

    def import_file_udbf(self, sid: str, stream_name: str, file: bytes) -> requests.Response | None:
        """
        Imports a UDBF file using the HTTP API.

        Args:
            file (bytes): The UDBF file content to be imported.

        Returns:
            Optional[requests.Response]: The server response if the request is successful,
             otherwise None.
             :param file:
             :param stream_name:
             :param sid:
        """
        self._create_import_session_udbf(sid, stream_name)
        if not self.import_session_res_udbf or "Data" not in self.import_session_res_udbf:
            logging.error("Import session not initialized. Please create an import session first.")
            return None

        self.session_ID = str(self.import_session_res_udbf["Data"]["SessionID"])
        url_list = f"{self.url}/history/data/import/{self.session_ID}"
        header_list = {
            "Content-Type": "application/octet-stream",
            "Authorization": f"Bearer {self.login_token['access_token']}",
        }
        try:
            res = requests.post(url_list, headers=header_list, data=file)
            if res.status_code == 200:
                logging.info("UDBF file successfully imported.")
                return res
            else:
                logging.error(
                    f"Import failed! Response Code: {res.status_code}, Reason: {res.reason}"
                )
        except requests.RequestException as err:
            logging.error(f"Failed to import UDBF file: {err}")

        return None

    # csv importer
    def create_import_session_csv(
        self,
        stream_ID: str,
        stream_Name: str,
        csv_config: CsvConfig,
        create_meta_data: bool = True,
        session_timeout: int = 60,
    ) -> requests.Response | None:
        """
        Creates an import session for a CSV file using the HTTP API.

        Args:
            stream_ID (str): The stream ID.
            stream_Name (str): The buffer name for the new stream.
            csv_config (CsvConfig): Configuration settings for the CSV import.
            create_meta_data (bool, optional): Whether to automatically create metadata.
            Defaults to True.
            session_timeout (int, optional): Session timeout in seconds. Defaults to 60.

        Returns:
            Optional[requests.Response]: The server response if the request is successful,
            otherwise None.
        """
        url_list = f"{self.url}/history/data/import"
        param = {
            "Type": "csv",
            "SourceID": stream_ID,
            "SourceName": stream_Name,
            "MeasID": "",
            "SessionTimeoutSec": str(session_timeout),
            "AddTimeSeries": "false",
            "SampleRate": "-1",
            "AutoCreateMetaData": str(create_meta_data).lower(),
            "CSVSettings": csv_config.get_config(),
        }

        try:
            logging.debug(f"CSV import parameters: {param}")
            res = requests.post(url_list, headers=self.headers, json=param)
            if res.status_code == 200:
                self.import_session_res_csv = res.json()
                self.import_session_csv_current = {
                    "stream_id": stream_ID,
                    "ts": time.time(),
                    "timeout": session_timeout,
                }
                return res
            else:
                logging.error(
                    f"Creating import session failed! "
                    f"Response Code: {res.status_code}, Reason: {res.reason}"
                )
        except requests.RequestException as e:
            logging.error(f"Failed to create import session: {e}")

        return None

    def __import_file_csv(self, file: bytes) -> requests.Response | None:
        """
        Imports a CSV file using the HTTP API.

        Args:
            file (bytes): The content of the CSV file to be uploaded.

        Returns:
            Optional[requests.Response]: The server response if the request is successful,
            otherwise None.
        """
        if not self.import_session_res_csv or "Data" not in self.import_session_res_csv:
            logging.error("Import session not initialized. Please create an import session first.")
            return None

        self.session_ID = str(self.import_session_res_csv["Data"]["SessionID"])
        url_list = f"{self.url}/history/data/import/{self.session_ID}"
        headers = {
            "Content-Type": "text/csv",
            "Authorization": f"Bearer {self.login_token['access_token']}",
        }

        try:
            res = requests.post(url_list, headers=headers, data=file)
            if res.status_code == 200:
                logging.info("CSV file successfully imported.")
                return res
            else:
                logging.error(
                    f"Import failed! Response Code: {res.status_code}, Reason: {res.reason}"
                )
        except requests.RequestException as e:
            logging.error(f"Failed to import CSV file: {e}")

        return None

    def upload_csv_file(
        self,
        stream_name: str,
        file_path: str,
        py_formatter: str | None = None,
        csv_config: CsvConfig | None = None,
    ) -> str | None:
        """
        Performs preparatory functions for CSV import.

        Args:
            stream_name (str): The name of the stream to upload the CSV to.
            file_path (str): The path of the CSV file to be uploaded.
            py_formatter (Optional[str], optional): Python-specific date format if
            different from the backend format.
            py_formatter is delivered if python parses dates differently than c++ (backend parsing)
            e.g. py_formatterClmn1 = "%d.%m.%Y %H:%M:%S.%f" for python,
            while DateTimeFmtColumn1: str = "%d.%m.%Y %H:%M:%S.%F" for API config
            csv_config (Optional[CsvConfig], optional): Configuration settings for the CSV import.

        Returns:
            Optional[str]: The stream ID if the upload is successful, otherwise None.
        """
        # **************************************
        #    Read and check the CSV file
        # **************************************
        try:
            # Use the Python formatter if provided, otherwise use the default from csv_config
            if py_formatter is None:
                py_formatterClmn1 = self.csv_config.DateTimeFmtColumn1

            first_lines = pd.read_csv(file_path, encoding="utf-8", nrows=10, sep=";")
            read_date = first_lines.iat[self.csv_config.ValuesStartRowIndex - 1, 0]
            read_date = Helpers.remove_hex_from_string(read_date)

            # Parse the date and time based on the configuration
            if not self.csv_config.DateTimeFmtColumn2 and not self.csv_config.DateTimeFmtColumn3:
                date_time_obj = dt.datetime.strptime(
                    read_date + ";",
                    py_formatterClmn1 + ";" + self.csv_config.DateTimeFmtColumn2,
                )
            elif self.csv_config.DateTimeFmtColumn2:
                read_time = first_lines.iat[self.csv_config.ValuesStartRowIndex - 1, 1]
                date_time_obj = dt.datetime.strptime(
                    read_date + ";" + read_time,
                    py_formatterClmn1 + ";" + self.csv_config.DateTimeFmtColumn2,
                )

            # Convert to UTC and then to the target timezone
            csv_timestamp_utc = date_time_obj.replace(tzinfo=tz.gettz("UTC"))
            csv_timestamp_local = csv_timestamp_utc.astimezone(tz.gettz("Europe/Paris"))
            csv_timestamp = dt.datetime.timestamp(csv_timestamp_local)
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            return None
        except Exception as e:
            logging.error(f"Could not read the CSV file. Please check the configuration: {e}")
            return None

        # Log the first CSV timestamp
        timestamp_tmp = dt.datetime.fromtimestamp(csv_timestamp)
        logging.info(
            f"First CSV timestamp: {csv_timestamp}, {timestamp_tmp.strftime('%d.%m.%Y %H:%M:%S')}"
        )

        # **************************************
        #    Check if stream exists
        # **************************************
        if (self.streams is not None and
                any(stream.name == stream_name for stream in self.streams.values())):
            for stream_id, stream in self.streams.items():
                if stream.name == stream_name:
                    write_ID = stream.id
                    reprise = 1
                    logging.info(
                        f"Stream already exists in GI.Cloud. "
                        f"Continuing import for stream ID: {write_ID}"
                    )
        else:
            write_ID = str(uuid.uuid4())
            reprise = 0
            logging.info(
                f"Stream not found in GI.Cloud. Initializing import for new stream ID: {write_ID}"
            )

        # Validate UUID
        if not utils.is_valid_uuid(write_ID):
            logging.error(f"Invalid UUID: {write_ID}")
            return None

        # **************************************
        #    Check last imported timestamps
        # **************************************
        if reprise == 1 and self.streams is not None:
            try:
                for _, stream in self.streams.items():
                    if stream.name == stream_name:
                        last_timestamp = stream.last_ts
                        timestamp_end_s = dt.datetime.utcfromtimestamp(last_timestamp / 1000)
                        logging.info(
                            f"Last UTC imported timestamp:"
                            f" {(last_timestamp / 1000)}, {timestamp_end_s.strftime('%Y-%m-%d %H:%M:%S')}"
                        )
            except AttributeError:
                logging.warning("Stream exists but no last timestamp found.")
                last_timestamp = 0
        else:
            last_timestamp = 0
            logging.info(f"Stream is empty. Last timestamp: {last_timestamp}")

        # **************************************
        #    Upload the file
        # **************************************
        csv_config = csv_config or self.csv_config

        if csv_timestamp > last_timestamp / 1000:
            # Reuse import session if possible
            if not self.__import_session_valid(write_ID):
                self.create_import_session_csv(write_ID, stream_name, csv_config)

            try:
                with open(file_path, "rb") as f:
                    data_upload = f.read()

                response = self.__import_file_csv(data_upload)

                if response and response.status_code == 200:
                    logging.info(f"Import of {file_path} was successful")
                    return write_ID
                else:
                    logging.error(
                        f"Import failed! Response Code:"
                        f" {response.status_code if response else 'N/A'}, "
                        f"Reason: {response.reason if response else 'No response'}"
                    )
            except Exception as e:
                logging.error(f"Error during file upload: {e}")
        else:
            logging.error(
                "Import failed: The first CSV value is before the last database timestamp. "
                "The import must begin after the last timestamp."
            )

        return None

    def __import_session_valid(self, stream_id: str) -> bool:
        """
        Checks if the current import session is valid for the given stream ID.

        Args:
            stream_id (str): The stream ID to check.

        Returns:
            bool: True if the import session is valid, False otherwise.
        """
        if self.import_session_csv_current is None:
            return False

        session = self.import_session_csv_current
        session_is_valid = (
            session["stream_id"] == stream_id
            and (session["ts"] - time.time()) + 5 < session["timeout"]
        )

        return session_is_valid

    def delete_import_session(self) -> requests.Response | None:
        """
        Deletes the current import session using the HTTP API.

        Returns:
            Optional[requests.Response]: The server response if the request is successful,
             otherwise None.
        """
        if not self.session_ID:
            logging.error("No import session ID found. Cannot delete session.")
            return None

        url_list = f"{self.url}/history/data/import/{self.session_ID}"
        headers = {"Authorization": f"Bearer {self.login_token['access_token']}"}

        try:
            res = requests.delete(url_list, headers=headers)
            if res.status_code == 200:
                logging.info("Import session closed successfully.")
                return res
            else:
                logging.error(
                    f"Failed to close import session! "
                    f"Response Code: {res.status_code}, Reason: {res.reason}"
                )
        except requests.RequestException as e:
            logging.error(f"Failed to delete import session: {e}")

        return None

    # Read and Write Single Values out of live datastreams
    # Notice postprocessed data do not work with this functions !

    def read_value(self, var_ids: List[str]) -> List[Any] | None:
        """
        Reads online values for a list of variable IDs.

        Args:
            var_ids (List[str]): A list of variable IDs.
            For example, var_ids=["47f32894-c6a0-11ea-81a1-02420a000368"].

        Returns:
            Optional[List[Any]]: A list of current live values if the request is successful,
            otherwise None.
        """
        url_list = f"{self.url}/online/data"
        param = {"Variables": var_ids, "Function": "read"}

        try:
            res = requests.post(url_list, headers=self.headers, json=param)
            if res.status_code == 200:
                current_live_value = res.json()
                logging.info(f"Current live value: {current_live_value}")
                return current_live_value
            else:
                logging.error(
                    f"Failed to read value! Response Code: {res.status_code}, Reason: {res.reason}"
                )
        except requests.RequestException as e:
            logging.error(f"Request error while reading value: {e}")

        return None

    def write_value_on_channel(self, var_ids: List[str], write_list: List[Any]) -> dict | None:
        """
        Writes values to a list of variable IDs.

        Args:
            var_ids (List[str]): A list of variable IDs.
            For example, var_ids=["47f32894-c6a0-11ea-81a1-02420a000368"].
            write_list (List[Any]): A list of values to write. For example, write_list=["0"].

        Returns:
            Optional[dict]: The server response as a dictionary if the request is successful,
            otherwise None.
        """
        url_list = f"{self.url}/online/data"
        param = {
            "Variables": var_ids,
            "Values": write_list,
            "Function": "write",
        }

        try:
            res = requests.post(url_list, headers=self.headers, json=param)
            if res.status_code == 200:
                write_value_res = res.json()
                logging.info("Data successfully written.")
                return write_value_res
            else:
                logging.error(
                    f"Failed to write data! Response Code: {res.status_code}, Reason: {res.reason}"
                )
        except requests.RequestException as e:
            logging.error(f"Request error while writing data: {e}")

        return None

    def get_gistreamvariables(self, stream: str, variables: List[str]) -> List[GIStreamVariable]:
        """
        Retrieves GIStreamVariable instances for the given stream and variable names.

        Args:
            stream (str): The stream name.
            variables (List[str]): A list of variable names.

        Returns:
            List[Optional[GIStreamVariable]]: A list of GIStreamVariable instances if found,
            otherwise None for each not found.
        """
        gi_vars = []
        for var in variables:
            result = self.find_var(f"{stream}__{var}")
            if result:
                gi_vars.append(list(result.values())[0])
        return gi_vars

    def get_buffer_data(
        self,
        start: int,
        end: int,
        variables: List[Variable],
        points: int = 1_000_000,
        data_type: DataType = DataType.EQUIDISTANT,
        data_format: DataFormat = DataFormat.JSON,
        precision: str = "-1",
        timezone: str = "Europe/Vienna",
        timeoffset: int = 0,
        csv_settings: Optional[CSVSettings] = None,
        log_settings: Optional[LogSettings] = None,
        target: Optional[str] = None,
    ) -> Union[Dict, bytes]:
        """
        Fetch data from a buffer data source via API.

        Parameters:
        - start (int): Start time in ms. Use negative value if relative to 'End'.
        - end (int): End time in ms. Use 0 for 'End'.
        - variables (List[Variable]): List of variables with keys 'SID', 'VID', 'Selector'.
        - points (int): Number of data points. Default is 655.
        - data_type (DataType): Data type. Default is DataType.EQUIDISTANT.
        - data_format (DataFormat): Data format. Default is DataFormat.JSON.
        - precision (str): Precision. Default is '-1'.
        - timezone (str): Timezone specifier, e.g., 'Europe/Vienna'.
        - timeoffset (int): Time offset in seconds. Default is '0'.
        - csv_settings (Optional[CSVSettings]): Configuration for CSV format.
        Required if data_format is DataFormat.CSV.
        - log_settings (Optional[LogSettings]): Configuration for UDBF format.
        Required if data_format is DataFormat.UDBF.
        - target (Optional[str]): For DataFormat.UDBF format. Options: 'file', 'record'.

        Returns:
        - Union[Dict, str, bytes]: The response data from the API.

        Raises:
        - requests.HTTPError: If the API request fails.
        - ValueError: If required parameters are missing.
        """

        url = f"{self.url}/buffer/data"

        # Validate required parameters
        if not variables:
            raise ValueError("The 'variables' parameter must be a non-empty list.")

        if data_format == DataFormat.CSV and not csv_settings:
            logging.info("'csv_settings' can be configured when data_format is DataFormat.CSV.")

        if data_format == DataFormat.UDBF and not log_settings:
            logging.info("'log_settings' can be configured when data_format is DataFormat.UDBF.")

        payload: Dict[str, Union[str, int, List[Variable], CSVSettings, LogSettings]] = {
            "Start": start,
            "End": end,
            "Variables": variables,
            "Points": points,
            "Type": data_type.value,
            "Format": data_format.value,
            "Precision": precision,
            "TimeZone": timezone,
            "TimeOffset": timeoffset,
        }

        if csv_settings:
            payload["CSVSettings"] = csv_settings

        if log_settings:
            payload["LogSettings"] = log_settings

        if data_format == DataFormat.UDBF and target:
            payload["Target"] = target

        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()

        if data_format in {DataFormat.COL, DataFormat.ROW, DataFormat.JSON}:
            return response.json()
        else:
            # Results given in bytes
            return response.content
