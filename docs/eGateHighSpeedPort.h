//////////////////////////////////////////////////////////////////////////////////////////
/*																						*/
/*   WARNING: Do not add to, delete from, or otherwise modify the contents				*/
/*            of this header file !!!!!!!!!!!!!!!!!!!!!!!!!								*/
/*																						*/
/*   COPYRIGHT    : (C) 2009 by Gantner instruments, all rights reserved !				*/
/*																						*/
/*------------------ INFO --------------------------------------------------------------*/
/*																						*/
/*	PROJECT      : eGateHighSpeedPort.dll int32_terface									*/
/*	FILE NAME    : eGateHighSpeedPort.h													*/
/*																						*/
/*	COMPILER     : MSVC++ 6.0															*/
/*	SYSTEM       : Windows95 / 98 / ME / NT / 2K / XP / VISTA / 7						*/
/*																						*/
/*	DATE         : 2009-07-14															*/
/*																						*/
/*																						*/
/*------------------ GENERAL INSTRUCTIONS ----------------------------------------------*/
/*																						*/
/*	C-Header-File to use with DLL.														*/
/*																						*/
/*	DLL DESCRIPTION:																	*/
/*																						*/
/*				This is a multithreading DLL which can handle up to 10 simultanous		*/
/*				connections.															*/
/*																						*/
/*				It can be used by several processes (programs) at the same time			*/
/*				independently.															*/
/*				In special cases, differen processes can exchange signals				*/
/*				through the DLL.														*/
/*																						*/
/*				Every connection has to be created with "_CD_eGateHighSpeedPort_Init"	*/
/*				first.																	*/
/*				Then a connection index and a client index has to be stored, to be able	*/
/*				to select the correct connection again (both should be -1 before init).	*/
/*																						*/
/*				connection index:														*/
/*																						*/
/*					If the same IP address or communication type was not already		*/
/*					initialized before, "connection index" will return a new value		*/
/*					to be able to use exactly this connection later.					*/
/*																						*/
/*					If connection index and communication type are already initialized,	*/
/*					"_CD_eGateHighSpeedPort_Init" will return a new client index.		*/
/*					In this case, be sure that all clients are really used!!			*/
/*																						*/
/*				client index:				(only neccessary for special cases)			*/
/*																						*/
/*					Within one process, several "clients" can be registered by calling	*/
/*					"_CD_eGateHighSpeedPort_Init" with the same IP address and 			*/
/*					connection type.													*/
/*					This can be used to access data synchronous from different threads 	*/
/*					or functions within the process the DLL was called.					*/
/*																						*/
/*					E.g.: a new data frame from a buffered connection is only available */
/*					when all registered clients in this process have read it.			*/
/*																						*/
/*				Return Codes:															*/
/*																						*/
/*					Only a few return codes are really used like HSP_OK, HSP_ERRPR,		*/
/*					HSP_NOT_READY or HSP_NO_FILE.										*/
/*																						*/
/*					If a function with General Return codes returns HSP_ERROR,			*/
/*					something went wrong.												*/
/*					Then "_CD_eGateHighSpeedPort_ExplainError" can be used to get more	*/
/*					info's in plain text;												*/
/*																						*/
/*	ATTENTION:	All strings need to have a terminating 0 at the end !!!!				*/
/*																						*/
/*------------------ CHANGES -----------------------------------------------------------*/
/*																						*/
/*  V1.0.0.0   Implementation;															*/
/*			   Online communication														*/
/*																						*/
/*  V2.0.0.0   CircleBuffer communication implemented									*/
/*			   Connection Synchronisation implemented									*/
/*			   MDF Storage (MDFlib) implemented											*/
/*																						*/
/*	V2.0.0.1   Bug fixed at channel index resolution for online communication			*/
/*																						*/
/*  V2.0.0.7   Compatibility for e.gate/e.pac (V2) (only online communication)			*/
/*			   Bug fixed: Free connection correctly while closing the last client		*/
/*																						*/
/*	V2.0.0.8   Callbacks implemented for Error handling and DLL communication			*/
/*			   Shared memory implemented for int32_ter progrm data exchange via DLL		*/
/*																						*/
/*	V2.0.0.9   ASCII Data Storage implemented											*/
/*																						*/
/*  V2.0.1.0   Online communication via DistributorPort UDP implemented					*/
/*																						*/
/*	V2.0.1.1   New File transfer Functions implemented									*/	
/*																						*/
/*	V2.0.1.2   DLL debug functions added: If any program registers the debug callback	*/
/*			   The dll will invoke the callback function if new debug info's are		*/
/*			   Available.																*/
/*																						*/
/*	V2.0.1.3   ASCII storage date/time parameters for file name use the first timestamp	*/
/*			   Read Buffer: if Timestamp==OLETime -> precision=8 else -> precision=0	*/		
/*			   If connection state is called, dll now communicates -> keeps connection	*/	
/*																						*/
/*	V2.0.1.4   BackTime is now saved that it can be used after reconnect.				*/
/*																						*/
/*	V2.0.1.5   Improvements at handling different connections and clients.				*/
/*			   AutoSyncMode implemented. If enabled, buffer will be deleted				*/
/*			   until timestamps are similar.											*/
/*																						*/
/*	V2.0.1.6   Bug eliminated at ASCII storage: Time error at filename generation		*/
/*			   Bug eliminated: DLL now recognizes PC Time Backsteps and won't hang		*/
/*																						*/
/*	V2.0.1.7   Bug eliminated: ReadBuffer Function didn't indicate connection loss		*/
/*			   correctly.																*/
/*																						*/	
/*	V2.0.1.8   New sleep function "eGateHighSpeedPort_SleepMS" added					*/		
/*																						*/
/*	V2.0.1.9   New function "eGateHighSpeedPort_ReadBufferToDoubleArray"			    */	
/*			   Version is tested for Q.Station connection								*/	
/*			   Bug eliminated at checking Endianess from #summary.sta file				*/	
/*	V2.0.2.0																		    */
/*			   New Device Info types added												*/
/*			   Bug eliminated at reconnecting different controllers						*/
/*			   Bug eliminated at writing to int32_t16 output channels					*/
/*			   Bug eliminated at writing when empty channels are used					*/
/*			   Added function WriteOnline_Single_Immediate								*/
/*			   Bug eliminated at unsigned int32_t data types							*/
/*			   Bug eliminated with square brackets in ini-file values					*/
/*			   ReadBufferToDoubleArray_StraightTimestamp added							*/
/*			   Changed buffer decoding that timestamp is not neccessary					*/
/*	V2.0.2.1																			*/
/*			   Bug eliminated: connection wasn't cleaned up correctly when TCP/IP		*/
/*             connection was already closed by the device								*/
/*			   Removed bugs	with PImage > 1024 bytes									*/
/*			   Added cleanup for remaining buffer data when connection is closed	    */
/*																						*/
/*	V2.0.2.2																			*/
/*			   Bug eliminated: TotalFrameLength wasn't correctly decoded				*/
/*			   from #summary.sta file													*/
/*			   Increased number of max connections from 10 to 20						*/
/*			   Fixed bug that Channel - Unit sometimes had invalid/old value			*/
/*																						*/
/*	V3.0.0.1  																			*/
/* 			   Complete new implementation based on GInsData Interface					*/
/*			   Added platform support: windows amd64, linux x86, linux amd64,			*/
/*             ARM, ANDROID																*/
/*			   Diagnostic:																*/
/* 			   		Fixed bug with wrong error counter order if internal variables 		*/
/* 					were used.															*/
/* 					Replaced unused diagnostic value "states" with "cycleCount" because	*/
/* 					Q.station can sample devices with different cycle rates.			*/
/*			   Added functions: eGateHighSpeedPort_ReadBuffer_Single_RawType			*/
/*						        eGateHighSpeedPort_ReadOnline_Frame						*/
/*						        eGateHighSpeedPort_ReadOnline_FrameToDoubleArray		*/
/*             Added device info types:	MID, BufferCount, LoggerCount , Timestamp Type	*/
/*																						*/
/*	V3.0.2.0 																			*/
/*             Added PostProcessBuffer features to access buffers on GI.bench 			*/
/*			   Fixed problem if sample rate of certain sources is <0>					*/
/*	V3.0.3.0																			*/
/*             Fixed problem that data rate could not be read correctly.	 			*/
/*			   Added possibility to read TimestampVariable also from device interface.	*/
/*			   Fixed bug when reading out variable list from HeaderInterface.			*/
/*			   Changed library interface for linux that internal functions are not 		*/
/*			   exposed any more.														*/
/* 			   (caused incompatibility on platforms with diffenrent libstdc++)			*/
/*	V3.0.4.0																			*/
/*			   Removed deprecated data storage functions 								*/
/*																						*/				
//////////////////////////////////////////////////////////////////////////////////////////
/*--------------------------------------------------------------------------------------*/

#pragma once

#ifdef __cplusplus
extern  "C" {
#endif

#ifdef _WIN32
	#ifdef EGATEHIGHSPEEDPORT_EXPORTS
	#define EGATEHIGHSPEEDPORT_API __declspec(dllexport)
	#else
	#define EGATEHIGHSPEEDPORT_API __declspec(dllimport)
	#endif

	#define CALLINGCONVENTION_CD __cdecl
	#define CALLINGCONVENTION_SC __stdcall

	#ifndef CALLBACK
	#define CALLBACK __stdcall
	#endif
#else
	#define EGATEHIGHSPEEDPORT_API __attribute__((visibility("default")))
	#define CALLINGCONVENTION_CD
	#define CALLINGCONVENTION_SC
#endif

//////////////////////////////////////////////////////////////////////////////////////////
/*----------------- Global Constants ---------------------------------------------------*/

#define COMPILE_DEMO_DLL_OFF

//////////////////////////////////////////////////////////////////////////////////////////
/*----------------- General return codes ------------------------------------------------*/
#define HSP_OK					0
#define HSP_ERROR				1
#define HSP_CONNECTION_ERROR	2
#define HSP_INIT_ERROR			3
#define HSP_LIMIT_ERROR			4
#define HSP_SYNC_CONF_ERROR		5
#define HSP_MULTYUSED_ERROR		6
#define HSP_INDEX_ERROR			7
#define HSP_FILE_ERROR			8
#define HSP_NOT_READY			9
#define HSP_EXLIB_MISSING		10
#define HSP_NOT_CONNECTED		11
#define HSP_NO_FILE				12
#define HSP_CORE_ERROR			13
#define HSP_POINTER_INVALID		14
#define HSP_NOT_IMPLEMENTED		15
#define HSP_INVALID_TIMESTAMP	16
/*----------------- ChannelInfo ID's ---------------------------------------------------*/
//String:
#define CHINFO_NAME				0	// = Channel name
#define CHINFO_UNIT				1	// = Unit (°C, m, kg,...)
#define CHINFO_DADI				2	// = Data direction (Input, Output, Empty,..)
#define CHINFO_FORM				3	// = e.g.: %8.3
#define CHINFO_TYPE				4	// = FLOAT, DOUBLE,...
#define CHINFO_VART				33	// = Variable Type (AIN, AOU,..)
//intteger:
#define CHINFO_INDI				5	// = Input access Index
#define CHINFO_INDO				6	// = Output access Index
#define CHINFO_INDX				7	// = Total access index
#define CHINFO_PREC				8	// = precision
#define CHINFO_FLEN				9	// = field length
#define CHINFO_RMIN				30	// = Range min
#define CHINFO_RMAX				31  // = Range max
#define CHINFO_MIND				32  // = Module Index
#define CHINFO_DTYI				34	// = Data Type Index

/*----------------- DeviceInfo ID's ---------------------------------------------------*/
//String
#define DEVICE_LOCATION			10
#define DEVICE_ADDRESS			11
#define DEVICE_TYPE				12
#define DEVICE_TYPENAME			DEVICE_TYPE
#define DEVICE_VERSION			13
#define DEVICE_TYPECODE			14
#define DEVICE_SERIALNR			15
//integer
#define DEVICE_SAMPLERATE		16
#define DEVICE_MODULECOUNT		17
#define DEVICE_CHANNELCOUNT		18
#define	DEVICE_MID				50
#define DEVICE_BUFFERCOUNT		51
#define	DEVICE_LOGGERCOUNT		52
#define DEVICE_TSTYPE			53
/*----------------- SlaveModuleInfo ID's ----------------------------------------------*/
//String
#define MODULE_TYPE				19
#define MODULE_TYPECODE			20
#define MODULE_Location			21
//integer
#define MODULE_UARTINDEX		22
#define MODULE_ADDRESS			23
#define MODULE_VARCOUNT			24
/*----------------- StorageInfo ID's ---------------------------------------------------*/
#define STORE_FILECOUNT			25
#define STORE_SECONDS			26
/*------------------ Buffer ID's -------------------------------------------------------*/
#define BUFFER_MAXFRAMES		27
/*----------------- Data direction ID's ------------------------------------------------*/
#define DADI_INPUT				0   // = Input
#define DADI_OUTPT				1   // = Output
#define DADI_INOUT				2   // = Input/output
#define DADI_EMPTY				3   // = Empty
#define DADI_STATS				4	// = Statistic Channels
/*----------------- Connection Types ---------------------------------------------------*/
#define	HSP_ONLINE				1
#define	HSP_BUFFER				2
#define	HSP_ECONLOGGER			3
#define HSP_ARCHIVES			4
#define	HSP_FILES				5
#define HSP_DIAG				7
#define DLL_CONTROL				9
#define HSP_DIRECT				7
#define HSP_POSTPROCBUFFER		8
#define HSP_BUFFER0				100
#define HSP_BUFFER1				101
//...
/*----------------- Statistic info Types -----------------------------------------------*/
#define STAT_CONNECTED			0
#define	STAT_STACKSIZE			1
#define	STAT_DECODETIME			2
/*----------------- Diagnostic Types ---------------------------------------------------*/
#define DIAG_CONTROLLER			0
#define DIAG_INTERFACE			1
#define DIAG_TRANSPORT			2
#define DIAG_VARIABLE			3
#define DIAG_ITEMCOUNT			4
/*----------------- Data storage Types -------------------------------------------------*/
#define STOR_MDF				0
#define STOR_CSV				1
/*----------------- Timestamp Types ----------------------------------------------------*/
#define TSTYPE_NO				0
#define	TSTYPE_COUNTER			1
#define TSTYPE_TIMEOLE2			2
#define TSTYPE_DCSYSTEMTIME		3
/*----------------- File Types ---------------------------------------------------------*/
#define FILE_DIR_ALL				0
#define FILE_FLASHAPPLICATION		1
#define FILE_FLASHDATA				2
#define FILE_USBDATA				3
#define	FILE_VIRTUALSTATE			4
#define	FILE_VIRTUALONLINEBUFFER	5
#define	FILE_VIRTUALCIRCLEBUFFER	6
#define FILE_VIRTUALARCHIVE			7
#define FILE_VIRTUALLOGGER			8
#define	FILE_IDENTIFY_BY_PATH		10
/*----------------- File Locations -----------------------------------------------------*/
#define LOC_LOCALE				0
#define LOC_CONTROLLER			1
/*----------------- Data Types ---------------------------------------------------------*/
#define DATY_NO					0
#define DATY_BOOL				1
#define DATY_SINT8				2
#define DATY_USINT8				3
#define DATY_SINT16				4
#define DAYT_USINT16			5
#define DATY_SINT32				6
#define	DATY_USINT32			7
#define DATY_FLOAT				8
#define DATY_SET8				9
#define DATY_SET16				10
#define DATY_SET32				11
#define DATY_DOUBLE				12
#define DATY_SINT64				13
#define DATY_USINT64			14
#define DATY_SET64				15
/*----------------- Variable kind ID's ------------------------------------------------*/
#define VARKIND_EMPTY				0
#define VARKIND_AnalogOutput		1
#define VARKIND_dAnalogInput		2
#define VARKIND_DigitalOutput		3
#define VARKIND_DigitalInput		4
#define VARKIND_Arithmetic			5
#define VARKIND_Setpoint			6
#define VARKIND_Alarm				7
#define VARKIND_PIDController		8
#define VARKIND_SignalConditioning	9
#define VARKIND_Remote				10
#define VARKIND_Reference			11
/*----------------- Callback Types -----------------------------------------------------*/
#define CALL_CONTROL			0
#define CALL_ERROR				1
#define CALL_DIAG				2
#define CALL_DSPDATA			3
#define CALL_FREADY				4
#define CALL_DEBUG				5
/*----------------- Remote Control Types -----------------------------------------------*/
#define REMOTE_START			0
#define REMOTE_STOP				1
#define REMOTE_END				2
/*----------------- System Limits ------------------------------------------------------*/
#ifdef COMPILE_DEMO_DLL_ON
	#define MAXCONNECTIONS		1
	#define MAXCLIENTS			1
#else
	#define MAXCONNECTIONS		20		// = Max connections for this DLL
	#define MAXCLIENTS			100		// = Max clients for one connection
#endif

#define MAXADDRESSLENGTH		100
#define	MAXDEBUGMESSAGELEN		1024

EGATEHIGHSPEEDPORT_API int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_TEST(int32_t test, int32_t command);
EGATEHIGHSPEEDPORT_API int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_TEST(int32_t test, int32_t command);

//////////////////////////////////////////////////////////////////////////////////////////
/*------------- Global Control ---------------------------------------------------------*/
/*																						*/
/*	Description:																		*/
/*																						*/
/*		Following functions provide possibilities for global setup						*/
/*																						*/
//////////////////////////////////////////////////////////////////////////////////////////	
/*--------------------------------------------------------------------------------------*/
/************		Initialize connection												
																					
		Initialize the Ethernet HighSpeedPort Connection to a Gantner-Instruments		
	    Controller.

 	IN:
		hostName		 ...  the ip address of the controller
		timeout			 ...  the connection timeout in seconds
		mode			 ...  the communication mode (see constants "Connection Types")

							  If HSP_ONLINE: this function initializes the complete
							  communication.

							  If HSP_BUFFER or HSP_LOGGER:
							  eGateHighSpeedPort_InitBuffer is needed to select the
							  buffer index before data transfer.

							  Other Communication types will only open the Port but
							  not initialize anything.
		sampleRate       ...  The sample rate for reading single or buffered data
							  from the controller.

							  HSP_ONLINE: up to 1000Hz (check System Health!)
							  HSP_BUFFER: 2Hz default (otherwise check System Health!)
								
							  since dll version V3 - not used
	OUT:
		client Instance	  ... If several tasks of the application uses the same connection,
							  some DLL functions need the client instance
							  for synchronisation.
		connectionInstance .. handle that identifies/selects a connection

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_Init(const char* hostName,
											  int32_t timeOutSec, 
											  int32_t mode,
											  int32_t sampleRateHz, 
											  int32_t* clientInstance, 
											  int32_t* connectionInstance);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_Init(const char* hostName,
											  int32_t timeOutSec, 
											  int32_t mode,
											  int32_t sampleRateHz, 
											  int32_t* clientInstance, 
											  int32_t* connectionInstance);


/*--------------------------------------------------------------------------------------*/
/************		enable/disable auto sync mode

		Buffered connections support automatic synchronisation of data streams.

		If different connections have hardware synchronized controllers, data streaming will
		start only with similar timestamps.

		Following sync settings should be used on the controller:

		- Qsync			... direct synchronisation between Q-series controller
		- IRIG/AFNOR	... synchronisation by external Clocks on DCF77 or GPS
		- SNTP			... synchronisation over Ethernet
		- NMEA			... synchronisation over GPS


		1	=	enabled
		0	=	disabled

		function not used since dll V3
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD	_CD_eGateHighSpeedPort_SetAutoSyncMode(int32_t connectionInstance, int32_t enable);

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC	SC_eGateHighSpeedPort_SetAutoSyncMode(int32_t connectionInstance, int32_t enable);

/*--------------------------------------------------------------------------------------*/
/************		Configure sample rate

		Modifies the sample rate at runtime.
		This sample rate only defines the int32_terval for reading data from the controller
		to the pc.
		Due to ethernet is not deterministic, this will not be an exact timing.
		It only helps to influence the rate how fast data is copied between Controller and PC.
		The exact measurement rate of the controller has to be configured with test.commander!

		IN:
			connectionInstance	...	to select the correct connection
			sampleRate			... sampleRate(Hz)

		RETURN:
			General return codes

			function not used since dll V3
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD	_CD_eGateHighSpeedPort_SetSampleRate(int32_t connectionInstance, int32_t sampleRateHz);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC	SC_eGateHighSpeedPort_SetSampleRate(int32_t connectionInstance, int32_t sampleRateHz);
/*--------------------------------------------------------------------------------------*/
/************		Read sample rate

		Read the sample rate as configured at "Init" or "Configure sample rate".

		IN:
			connectionInstance	...	to select the correct connection

		OUT:
			sampleRate			... sampleRate(Hz)

		RETURN:
			General return codes

			function not used since dll V3
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD	_CD_eGateHighSpeedPort_GetSampleRate(int32_t connectionInstance, int32_t *sampleRateHz);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC	SC_eGateHighSpeedPort_GetSampleRate(int32_t connectionInstance, int32_t *sampleRateHz);
/*--------------------------------------------------------------------------------------*/
/************		Get RTC 
	Read the current time of the device.
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_GetRTC(int32_t connectionInstance,
															uint16_t *year,
															uint8_t *month,
															uint8_t *day,
															uint8_t *hour,
															uint8_t *minute,
															uint8_t *second,
															uint16_t *millisecond);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_GetRTC(int32_t connectionInstance,
															uint16_t *year,
															uint8_t *month,
															uint8_t *day,
															uint8_t *hour,
															uint8_t *minute,
															uint8_t *second,
															uint16_t *millisecond);

/*--------------------------------------------------------------------------------------*/

/************		Set RTC
	Set the time on the device with a specified time, for example actual PC time.

	Take care that no other time synchronization is configured in the device!
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_SetRTC(int32_t connectionInstance,
															uint16_t year,
															uint8_t month,
															uint8_t day,
															uint8_t hour,
															uint8_t minute,
															uint8_t second,
															uint16_t millisecond);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_SetRTC(int32_t connectionInstance,
															uint16_t year,
															uint8_t month,
															uint8_t day,
															uint8_t hour,
															uint8_t minute,
															uint8_t second,
															uint16_t millisecond);
/*--------------------------------------------------------------------------------------*/
/************		Configure Receive Timeout

		At eGateHighSpeedPort_init(..) connection timeout and receive timeout are similar.
		This function configures the timeout for receiving data.
		The "winsock.h" function "select()" is used to generate the timeout
		-> no blocking while timeout

		IN:
			connectionInstance	...	to select the correct connection
			timeout				... receive timeout in seconds

		RETURN:
			General return codes

			function not used since dll V3
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_SetReceiveTimeout(int32_t connectionInstance, int32_t timeOut);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_SetReceiveTimeout(int32_t connectionInstance, int32_t timeOut);
/*--------------------------------------------------------------------------------------*/
/************		Read Receive Timeout

	Reads the timeout configured with "_CD_eGateHighSpeedPort_SetReceiveTimeout"

	IN:
		connectionInstance	...	to select the correct connection

	OUT:
		timeout				... receive timeout in seconds

	RETURN:
		General return codes


		function not used since dll V3
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_GetReceiveTimeout(int32_t connectionInstance, int32_t *timeOut);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_GetReceiveTimeout(int32_t connectionInstance, int32_t *timeOut);
/*--------------------------------------------------------------------------------------*/
/************		Close connection

	Closes an opened connection and terminates its worker threads.

	IN:
		connectionInstance	...	to select the correct connection
		clientInstance		... to select the correct client

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_Close(int32_t connectionInstance, int32_t clientInstance);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_Close(int32_t connectionInstance, int32_t clientInstance);




//////////////////////////////////////////////////////////////////////////////////////////
/*------------- PostProcess buffer server handling -------------------------------------*/
/*																						*/
/*	Description:																		*/
/*																						*/
/*		Following functions allow creation of PostProcess buffers / data stream			*/
/*		Depending on environmental settings, different data backends are supported   	*/
/*																						*/
//////////////////////////////////////////////////////////////////////////////////////////
/**
 * @brief Create new PostProcess buffer / SystemStream
 *
 * @param sourceID			source UUID (SID) of this buffer
 * @param sourceName		name of this buffer
 * @param sampleRateHz		the desired sample rate for this measurement
 * @param bufferSizeByte	the maximum size of this buffer in bytes
 * @param segmentSizeByte	the size of a buffer segment (if supported)
 * @param retentionTimeSec  data retention time of this buffer (if supported)
 * @param dataTypeIdent		only option possible: "raw"
 * @param bufferHandle		the result handle
 * @param errorMsg			buffer for error message text if not successful
 * @param errorMsgLen		length of the error message buffer
 *
 * @return General return codes
 */
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_PostProcessBufferServer_Create(const char* sourceID,
																				   const char* sourceName,
																				   double	   sampleRateHz,
																				   uint64_t	   bufferSizeByte,
																				   uint64_t	   segmentSizeByte,
																				   double	   retentionTimeSec,
																				   const char* dataTypeIdent,
																				   int32_t*    bufferHandle,
																				   char* 	   errorMsg,
																				   uint32_t	   errorMsgLen);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_PostProcessBufferServer_Create(const char* sourceID,
																			   	  const char* sourceName,
																			      double	  sampleRateHz,
																			      uint64_t	  bufferSizeByte,
																			      uint64_t	  segmentSizeByte,
																			      double	  retentionTimeSec,
																				  const char* dataTypeIdent,
																			      int32_t*    bufferHandle,
																				  char* 	  errorMsg,
																				  uint32_t	  errorMsgLen);
/*--------------------------------------------------------------------------------------*/
/**
 * @brief Create new UDBF file buffer
 *
 * @param fullFilePath		destination path on the local file system
 * @param sourceID			source UUID (SID) of this stream
 * @param sourceName		name of this stream
 * @param sampleRateHz		the desired sample rate for this measurement
 * @param maxLengthSeconds	the maximum length of a file in seconds
 * @param options			bitset for future options
 * @param bufferHandle		the result handle
 * @param errorMsg			buffer for error message text if not successful
 * @param errorMsgLen		length of the error message buffer
 *
 * @return General return codes
 *
 * @details					Similar than the previous PostProcessBuffer, but writes to UDBF files.
 *							FullFilePath is checked if a file name is set or if it is a directory.
 *							If maxLengthSeconds is not 0, a new file is created automatically when reaching this limit.
 *							Also depending on the length, a automatic file wrap is done at round times.
 *							If it is a directory, the file name will be the source name from the header.
 *							It it is a file name, date time information will be appended.
 *							In both cases, the full path will be created if not existing.
 */
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_PostProcessBufferServer_CreateUDBFFileBuffer(const char*	fullFilePath,
																									const char*	sourceID,
																									const char* sourceName,
																									double		sampleRateHz,
																									uint64_t	maxLengthSeconds,
																									uint16_t	options,
																									int32_t*    bufferHandle,
																									char* 		errorMsg,
																									uint32_t	errorMsgLen);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_PostProcessBufferServer_CreateUDBFFileBuffer(const char* fullFilePath,
																								const char* sourceID,
																								const char* sourceName,
																								double		sampleRateHz,
																								uint64_t	maxLengthSeconds,
																								uint16_t    options,
																								int32_t*    bufferHandle,
																								char* 		errorMsg,
																								uint32_t	errorMsgLen);
/*--------------------------------------------------------------------------------------*/
/**
 * @brief Add a variable definition to the PostProcess buffer / SystemStream
 *
 * @param bufferHandle		handle to the requested buffer
 * @param variableID
 * @param variableName
 * @param Unit
 * @param DataTypeCode
 * @param VariableKindCode
 * @param Precision
 * @param FieldLength
 * @param RangeMin
 * @param RangeMax
 * @param errorMsg			buffer for error message text if not successful
 * @param errorMsgLen		length of the error message buffer
 *
 * @return General return codes
 */
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_PostProcessBufferServer_AddVariableDefinition(int32_t bufferHandle,
																								  const char* variableID,
																				   	   	   	   	  const char* variableName,
																								  const char *Unit,
																								  int32_t DataTypeCode,
																								  int32_t VariableKindCode,
																								  uint16_t Precision,
																								  uint16_t FieldLength,
																								  double RangeMin,
																								  double RangeMax,
																								  char* errorMsg,
																								  uint32_t errorMsgLen);

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_PostProcessBufferServer_AddVariableDefinition(int32_t bufferHandle,
																								  const char* variableID,
																				   	   	   	   	  const char* variableName,
																								  const char *Unit,
																								  int32_t DataTypeCode,
																								  int32_t VariableKindCode,
																								  uint16_t Precision,
																								  uint16_t FieldLength,
																								  double RangeMin,
																								  double RangeMax,
																								  char* errorMsg,
																								  uint32_t errorMsgLen);
/*--------------------------------------------------------------------------------------*/
/**
 * @brief Initialize Post Process Buffer
 *
 * @param bufferHandle		handle to the requested buffer
 * @param tempBufferLength	number of temporary buffer frames to be allocated internally
 * @param errorMsg			buffer for error message text if not successful
 * @param errorMsgLen		length of the error message buffer
 *
 * @return General return codes
 *
 * @details This function finalize the configuration and really creates the buffer.\n
 * 			If successful, data can be appended to the buffer.
 * 			There is also the possibility to allocate an internal frame buffer,
 * 			which geometry automatically fits to the actual buffer configuration.
 */
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_PostProcessBufferServer_Initialize(int32_t bufferHandle,
																				       uint32_t frameBufferLength,
																					   char*	errorMsg,
																					   uint32_t errorMsgLen);

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_PostProcessBufferServer_Initialize(int32_t bufferHandle,
																					  uint32_t frameBufferLength,
																					  char*		errorMsg,
																					  uint32_t	errorMsgLen);
/*--------------------------------------------------------------------------------------*/
/**
 * @brief Write data to internal frame buffer
 *
 * @param bufferHandle		handle to the requested buffer
 * @param frameIndex		index of the frame
 * @param variableIndex		index of variable
 * @param valueDouble		variable value
 * @param errorMsg			buffer for error message text if not successful
 * @param errorMsgLen		length of the error message buffer
 *
 * @return General return codes
 */
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_PostProcessBufferServer_WriteDoubleToFrameBuffer(int32_t bufferHandle,
																								  uint32_t   frameIndex,
																								  uint32_t 	 variableIndex,
																								  double   	 valueDouble,
																								  char* 	 errorMsg,
																								  uint32_t 	 errorMsgLen);

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC _SC_eGateHighSpeedPort_PostProcessBufferServer_WriteDoubleToFrameBuffer(int32_t bufferHandle,
																								  uint32_t   frameIndex,
																								  uint32_t 	variableIndex,
																								  double   	valueDouble,
																								  char* 	errorMsg,
																								  uint32_t 	errorMsgLen);
/*--------------------------------------------------------------------------------------*/
/**
 * @brief Write timestamp to internal frame buffer
 *
 * @param bufferHandle		handle to the requested buffer
 * @param frameIndex		index of the frame
 * @param valueInt			timestamp value as nano seconds since 01.01.2000
 * @param errorMsg			buffer for error message text if not successful
 * @param errorMsgLen		length of the error message buffer
 *
 * @return General return codes
 */
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_PostProcessBufferServer_WriteTimestampToFrameBuffer(int32_t bufferHandle,
																							  uint32_t   frameIndex,
																							  uint64_t 	valueInt,
																							  char* 	errorMsg,
																							  uint32_t 	errorMsgLen);

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC _SC_eGateHighSpeedPort_PostProcessBufferServer_WriteTimestampToFrameBuffer(int32_t bufferHandle,
																							  uint32_t   frameIndex,
																							  uint64_t 	valueInt,
																							  char* 	errorMsg,
																							  uint32_t 	errorMsgLen);
/*--------------------------------------------------------------------------------------*/
/**
 * @brief Get the last timestamp from the stream
 *
 * @param bufferHandle		handle to the requested buffer
 * @param dcTime			if pointer is set, will be filled with nano seconds since 01.01.2000 
 * @param epochTimeMs		if pointer is set, will be filled with epoch time in milli seconds
 * @param ole2Time          if pointer is set, will be filled with ole2time / days since 01.01.1900
 * @param errorMsg			buffer for error message text if not successful
 * @param errorMsgLen		length of the error message buffer
 *
 * @return General return codes
 *
 * @details					This function is especially useful whenn writing data to cloud backend to check/ensure order of data
 */
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_PostProcessBufferServer_GetLastTimeStamp(int32_t	bufferHandle,
																							 uint64_t*	dcTime,
																							 uint64_t*	epochTimeMs,
																							 double*	ole2Time,
																							 char* 		errorMsg,
																							 uint32_t 	errorMsgLen);

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC _SC_eGateHighSpeedPort_PostProcessBufferServer_GetLastTimeStamp(int32_t	bufferHandle,
																							uint64_t*	dcTime,
																							uint64_t*	epochTimeMs,
																							double*		ole2Time,
																							char* 		errorMsg,
																							uint32_t 	errorMsgLen);
/*--------------------------------------------------------------------------------------*/
/**
 * @brief Append the internal temporary frame buffer to the post process buffer
 *
 * @param bufferHandle		handle to the requested buffer
 * @param errorMsg			buffer for error message text if not successful
 * @param errorMsgLen		length of the error message buffer
 *
 * @return General return codes
 */
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_PostProcessBufferServer_AppendFrameBuffer(int32_t bufferHandle,
																							 char* errorMsg,
																							 uint32_t errorMsgLen);

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_PostProcessBufferServer_AppendFrameBuffer(int32_t bufferHandle,
																							 char* errorMsg,
																							 uint32_t errorMsgLen);
/*--------------------------------------------------------------------------------------*/
/**
 * @brief Append data to PostProcess buffer / SystemStream
 *
 * @param bufferHandle		handle to the requested buffer
 * @param data				pointer to raw data to be appended
 * @param dataLength		length of data to be appended
 * @param errorMsg			buffer for error message text if not successful
 * @param errorMsgLen		length of the error message buffer
 *
 * @return General return codes
 */
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_PostProcessBufferServer_AppendDataBuffer(int32_t bufferHandle,
																							 const char* data,
																							 uint64_t dataLength,
																							 char* errorMsg,
																							 uint32_t errorMsgLen);

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_PostProcessBufferServer_AppendDataBuffer(int32_t bufferHandle,
																							const char* data,
																							uint64_t dataLength,
																							char* errorMsg,
																							uint32_t errorMsgLen);
/*--------------------------------------------------------------------------------------*/
/**
 * @brief Close post process buffer server
 *
 * @param bufferHandle		handle to the requested buffer
 * @param errorMsg			buffer for error message text if not successful
 * @param errorMsgLen		length of the error message buffer
 *
 * @return General return codes
 */
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_PostProcessBufferServer_Close(int32_t bufferHandle,
																				   char* errorMsg,
																				   uint32_t errorMsgLen);

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC _SC_eGateHighSpeedPort_PostProcessBufferServer_Close(int32_t bufferHandle,
																				   char* errorMsg,
																				   uint32_t errorMsgLen);

//////////////////////////////////////////////////////////////////////////////////////////
/*------------- Config Data ------------------------------------------------------------*/
/*																						*/
/*	Description:																		*/
/*																						*/
/*		Following functions provide config information	from a specific connection		*/
/*		The connection has to be initialized first										*/	
/*																						*/
//////////////////////////////////////////////////////////////////////////////////////////
/*--------------------------------------------------------------------------------------*/
/************		Get number of channels		

	Reads the number of channels of a specific connection and a specific data direction

	ATTENTION: Buffered connections will not show any output channels,
			   although they are configured on the device!!
			

	IN:
		connectionInstance	...	to select the correct connection
		directionID			... to select the channel direction:

								DADI_INPUT	-> Input channels
								DADI_OUTPT	-> Output channels
								DADI_INOUT	-> Input or output channels

	OUT:
		ChannelCount			Number of channels

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_GetNumberOfChannels(int32_t ConnectionInstance,
															 	 	 	uint32_t directionID,
																		uint32_t *ChannelCount);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_GetNumberOfChannels(int32_t ConnectionInstance,
															 	 	   uint32_t directionID,
																	   uint32_t *ChannelCount);
/*--------------------------------------------------------------------------------------*/
/************		Get device info											


	Can be used to get different system info's from a initialized connection.

	IN:
		connectionInstance	...	to select the correct connection
		typeID				...	to select the requested type:

								DEVICE_LOCATION		...	reads the device location to channelInfo[]
								DEVICE_ADDRESS		...	reads the ip Address to channelInfo[]
								DEVICE_TYPE			... reads the module type to channelInfo[]
								DEVICE_VERSION		...	reads the firmware version to channelInfo[]
								DEVICE_TYPECODE		...	reads the MK-Code to channelInfo[]
								DEVICE_SERIALNR		...	reads the serial number to channelInfo[]

								DEVICE_SAMPLERATE	... reads the sample rate to info
								DEVICE_MODULECOUNT	... reads the number of slave modules to info
								DEVICE_CHANNELCOUNT	... reads the number of channels to info

	OUT:
		info				... device info as int32_teger as selected with typeID
		channelInfo			... device info as string as selected with typeID

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_GetDeviceInfo(int32_t ConnectionInstance,
															  int32_t typeID,
															  int32_t Index,
															  double *info,
															  char* channelInfo);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_GetDeviceInfo(int32_t ConnectionInstance,
															 int32_t typeID,
															 int32_t Index,
															 double *info,
															 char* channelInfo);
/*--------------------------------------------------------------------------------------*/
/************		Get channel info - string											

	Reads channel specific text based info's by an type ID, the channel Index and direction.

	Use "_CD_eGateHighSpeedPort_GetNumberOfChannels" first to get the number of channels for the 
	desired data direction.

	Then read any neccessary info to the chanels by indexing within a loop.
	The channel order is strictly conform to the system configuration.

	The same DirectionID as for "_CD_eGateHighSpeedPort_GetNumberOfChannels" has to be used!!

	IN:
		connectionInstance	...	to select the correct connection
		typeID				...	type of info
		
								CHINFO_NAME	-> Channel name
								CHINFO_UNIT	-> Unit (°C, m, kg,...)	
								CHINFO_DADI	-> Data direction (Input, Output, Empty,..)
								CHINFO_FORM	-> Data type
								CHINFO_TYPE	-> Channel Type (analog, digital,..)

		directionID			...	similar to "_CD_eGateHighSpeedPort_GetNumberOfChannels"
		channelIndex		... to access the correct channel from the list
		channelInfo			... desired string based channel info

	OUT:
		channelInfo			...	channel info as string

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_GetChannelInfo_String(int32_t ConnectionInstance,
															   	   	      uint32_t typeID,
																		  uint32_t directionID,
																		  uint32_t channelIndex,
																		  char* channelInfo);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_GetChannelInfo_String(int32_t ConnectionInstance,
															   	   	     uint32_t typeID,
																		 uint32_t directionID,
																		 uint32_t channelIndex,
																		 char* channelInfo);
/*--------------------------------------------------------------------------------------*/
/************		Get channel info - int
Reads channel specific text based info's by an type ID, the channel Index and direction.

	Use "_CD_eGateHighSpeedPort_GetNumberOfChannels" first to get the number of channels for the 
	desired data direction.

	Then read any neccessary info to the chanels by indexing within a loop.
	The channel order is strictly conform to the system configuration.

	The same DirectionID as for "_CD_eGateHighSpeedPort_GetNumberOfChannels" has to be used!!

	IN:
		connectionInstance	...	to select the correct connection
		typeID				...	type of info
								CHINFO_INDI		-> Input access Index
								CHINFO_INDO		-> Output access Index
								CHINFO_INDX		-> Total access index
								CHINFO_PREC		-> precision
								CHINFO_FLEN		-> field length

		directionID			...	similar to "_CD_eGateHighSpeedPort_GetNumberOfChannels"
		channelIndex		... to access the correct channel from the list
		channelInfo			... desired numeric channel info

	OUT:
		channelInfo			...	channel info as int32_teger

	RETURN:
		General return codes
*/										
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_GetChannelInfo_Int(int32_t ConnectionInstance,
																   uint32_t typeID,
																   uint32_t directionID,
																   uint32_t channelIndex,
																   int32_t *ChannelInfo);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_GetChannelInfo_Int(int32_t ConnectionInstance,
																  uint32_t typeID,
																  uint32_t directionID,
																  uint32_t channelIndex,
																  int32_t *ChannelInfo);
//////////////////////////////////////////////////////////////////////////////////////////
/*------------- Online Communication ---------------------------------------------------*/
/*																						*/
/*	Description:																		*/
/*																						*/
/*		Following functions provide communication possibilities for online data.		*/
/*		The connection has to be initialized first and config data functions can be		*/
/*		used to read some channel informations first.									*/
/*																						*/
/*		The cyclic data transmission between controller and PC is done by the DLL.		*/
/*		The DLL only provides buffers containing double values,							*/
/*		which are already decoded.														*/
/*		Following functions provide read/write access to this DLL Buffers.				*/
/*																						*/
/*	Performance:																		*/
/*																						*/
/*		The cycle time for updating online values is defined by sampleRate at			*/
/*		initialisation.																	*/
/*		The timing is not very exact and the cycle time can be about 100Hz max			*/
/*																						*/
/*		It is recommended to use online data transfer functions for:					*/
/*																						*/
/*			- check values (e.g. to trigger buffer communications)						*/
/*			- slow controlling applications												*/
/*			- monitor static, or non high dynamic values								*/
/*			- write output channels														*/
/*																						*/
/*		For high dynamic values use buffer functions instead							*/
/*																						*/
/*		For fast controlling applications use DistributorPort functions instead			*/
/*																						*/
//////////////////////////////////////////////////////////////////////////////////////////
/*--------------------------------------------------------------------------------------*/
/************		Read online single channel											

	Read a single double value from a specific channel on the connection, selected 
	with connectionIndex.

	All channels(analoge, digital / floating point32_t, int32_teger, boolean,..)

	IN:
		connectionInstance	...	to select the correct connection
		channelIndex		... to access the correct channel from the list
								Here, always the total index is neccessary!!
								-> Use "eGateHighSpeedPort_GetChannelInfo_Int" to to convert 
								any IN, OUT or INOUT index to the correct total index;

	OUT:
		value				... the actual value of this channel converted to double

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD
_CD_eGateHighSpeedPort_ReadOnline_Single(int32_t connectionInstance,
										 int32_t channelIndex,
										 double* value );
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC 
SC_eGateHighSpeedPort_ReadOnline_Single(int32_t connectionInstance,
										int32_t channelIndex,
										double* value );
/*--------------------------------------------------------------------------------------*/
/************		Read online frame
	Reads a complete online frame to be stored internally and accessed with ReadOnline_Single

	IN:
		connectionInstance	...	to select the correct connection

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD
_CD_eGateHighSpeedPort_ReadOnline_Frame(int32_t connectionInstance);

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC
SC_eGateHighSpeedPort_ReadOnline_Frame(int32_t connectionInstance);
/*--------------------------------------------------------------------------------------*/
/************		Read online frame to double array

	Reads a complete or part of an online frame to a double array.
	No worker threads are needed, every call initiates TCP/IP communication.

	"eGateHighSpeedPort_Init" has to be used first!

	IN:
		connectionInstance	...	to select the correct connection
		arrayLength			... Number of elements in "valueArray"
								If "valueArray" is smaller than "arrayLength" this will cause a segfault!!!
		startIndex			... index of first variable to be read
								(this will be the first value in valueArray)
		channelCount		... Number of channels to be read starting from "startIndex"^.
								If channelCount is larger than arrayLength, only arrayLength channels will be read.
								Is channelCount is -1 or larger than the real number of channels, all channels will be read.
	OUT:
		valueArray			... Point32_ter to a double array with at least "ArrayLength" elements
								contains double converted values.

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD
_CD_eGateHighSpeedPort_ReadOnline_FrameToDoubleArray(int32_t connectionInstance, 
													 double *valueArray,
													 uint32_t arrayLength,
													 int32_t startIndex,
													 int32_t channelCount);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC
SC_eGateHighSpeedPort_ReadOnline_FrameToDoubleArray(int32_t connectionInstance,
													double *valueArray,
													uint32_t arrayLength,
													int32_t startIndex,
													int32_t channelCount);

/*--------------------------------------------------------------------------------------*/
/************		Read online multiple channels										

	Not supported

*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD 
_CD_eGateHighSpeedPort_ReadOnline_Window(int32_t connectionInstance,
										 uint32_t startIndex,
										 uint32_t number,
										 double* values[]);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC 
SC_eGateHighSpeedPort_ReadOnline_Window(int32_t connectionInstance,
										uint32_t startIndex,
										uint32_t number,
										double* values[]);
/*--------------------------------------------------------------------------------------*/
/************		Write online single channel	
										
	Write a single double value to a specific channel on the connection, selected 
	with connectionIndex.

	All channels(analoge, digital / floating point32_t, int32_teger, boolean,..)

	ATTENTION: All channels can be written one by one. They will be stored in the DLL output buffer
			   until "eGateHighSpeedPort_WriteOnline_ReleaseOutputData" is called for this connection.

	IN:
		connectionInstance	...	to select the correct connection
		channelIndex		... to access the correct channel from the list
								Here, always the total index is neccessary!!
								-> Use "eGateHighSpeedPort_GetChannelInfo_Int" to to convert 
								any IN, OUT or INOUT index to the correct total index;
		value				... the new value for this channel as double
								(will be converted to the correct data type on the device)

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD 
_CD_eGateHighSpeedPort_WriteOnline_Single(int32_t connectionInstance,
										  int32_t channelIndex, 
										  double value);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC 
SC_eGateHighSpeedPort_WriteOnline_Single(int32_t connectionInstance,
										 int32_t channelIndex, 
										 double value);
/*--------------------------------------------------------------------------------------*/
/************		Write online single channel	Immediate
										
	Write a single double value to a specific channel on the connection, selected 
	with connectionIndex immeadiately.

	All channels(analoge, digital / floating point32_t, int32_teger, boolean,..)

	IN:
		connectionInstance	...	to select the correct connection
		channelIndex		... to access the correct channel from the list
								Here, always the total index is neccessary!!
								-> Use "eGateHighSpeedPort_GetChannelInfo_int" to to convert 
								any IN, OUT or INOUT index to the correct total index;
		value				... the new value for this channel as double
								(will be converted to the correct data type on the device)

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_WriteOnline_Single_Immediate(int32_t connectionInstance,
															uint32_t channelIndex,
															double value);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_WriteOnline_Single_Immediate(int32_t connectionInstance,
																  uint32_t channelIndex,
																  double value);
/*--------------------------------------------------------------------------------------*/
/************		Release output value										

	Releases all bufered output values.
	This ensures that all channels are written simultaniously.
	-> function not implemented! use "WriteOnline_Window" instead

	IN:
		connectionInstance	...	to select the correct connection

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD 
_CD_eGateHighSpeedPort_WriteOnline_ReleaseOutputData(int32_t connectionInstance);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC 
SC_eGateHighSpeedPort_WriteOnline_ReleaseOutputData(int32_t connectionInstance);
/*--------------------------------------------------------------------------------------*/
/************		Write online multiple channels										

	Not supported

	Preliminary Version for testing reasons:

	This function writes multiple sequent OUTPUT-channels simultanuously

	IN:
		connectionInstance	...	to select the correct connection

		startIndex			... index of first OUTPUT variable to write (use Output-Var Index)

		size				... size of values-array -> number of sequent OUTPUT variables to write, beginning from "startIndex"

		valuesArray			... pointer to an array of double values. 


	RETURN:
		General return codes

*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD 
_CD_eGateHighSpeedPort_WriteOnline_Window(int32_t connectionInstance,
										  uint32_t startIndex,
										  uint32_t size,
										  double* valuesArray);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC 
SC_eGateHighSpeedPort_WriteOnline_Window(int32_t connectionInstance,
										 uint32_t startIndex,
									     uint32_t size,
										 double* valuesArray);
/*--------------------------------------------------------------------------------------*/
/************		Set client state
	IN:
		connection Index ...  identifies the connection
		client Index	 ...  identifies the client
		state			 ...  set "1" if reading finished.
							  DLL will set this state to zero if new data is
							  available.

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD 
_CD_eGateHighSpeedPort_SetClientState(int32_t connectionInstance,
									  uint32_t clientIndex,
									  uint32_t state);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC 
SC_eGateHighSpeedPort_SetClientState(int32_t connectionInstance,
									 uint32_t clientIndex,
									 uint32_t state);
/*--------------------------------------------------------------------------------------*/
/************		Get client state
 	IN:
			connection Index ...  identifies the connection

			client Index	 ...  identifies the client

	RETURN: 
			Requested client state
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD 
_CD_eGateHighSpeedPort_GetClientState(int32_t connectionInstance,
									  int32_t clientIndex);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC 
SC_eGateHighSpeedPort_GetClientState(int32_t connectionInstance,
									 int32_t clientIndex);
//////////////////////////////////////////////////////////////////////////////////////////
/*------------- Buffered Communication -------------------------------------------------*/
/*																						*/
/*	Description:																		*/
/*																						*/
/*		Following functions provide communication possibilities for buffered data.		*/
/*		Connection and buffer has to be initialized first and config data functions 	*/
/*		can beused to read some channel information's first.							*/
/*																						*/
/*		For initialisation, Communication type "HSP_BUFFER" or "HSP_ECONLOGGER" has		*/
/*		to be used:																		*/
/*																						*/
/*		HSP_BUFFER ..... read data from the int32_ternal circle buffer						*/
/*		HSP_ECONLOGGER . read data from a e.con dataLogger 								*/
/*																						*/
/*		The cyclic data transmission between controller and PC is done by the DLL.		*/
/*		The DLL only provides buffers containing double values,							*/
/*		which are already decoded.														*/
/*		Following functions provide read access to this DLL Buffers.					*/
/*																						*/
//////////////////////////////////////////////////////////////////////////////////////////
/*--------------------------------------------------------------------------------------*/
/************	Initialize Buffer
												    
	Initializes a buffered connection with a specified circular buffer or test.con
	dataLogger on a supported controller.

	Communication Type must be HSP_BUFFER or HSP_LOGGER.

	eGateHighSpeedPort_Init() has to be used first!!
	    																		
 	IN:
		connection connectionInstance	...	to select the correct connection
		buffer bufferIndex				... the index of a CircleBuffer or test.con Logger.
											Check configuration if the correct buffer type is supported
											and configured correctly!

	RETURN:
		General return codes
*/

EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_InitBuffer(int32_t connectionInstance,
														   	   int32_t bufferIndex,
															   int32_t autoRun);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_InitBuffer(int32_t connectionInstance,
														  	  int32_t bufferIndex,
															  int32_t autoRun);

/*--------------------------------------------------------------------------------------*/
/************		Get BostProcess buffer count
*
RETURN:
Number of available post process buffers
*/
EGATEHIGHSPEEDPORT_API
uint32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_GetPostProcessBufferCount();

EGATEHIGHSPEEDPORT_API
uint32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_GetPostProcessBufferCount();

/*--------------------------------------------------------------------------------------*/
/************		Initialize connection to PostProcess buffer
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_Init_PostProcessBuffer(const char* BufferID,
int32_t* clientInstance,
int32_t* connectionInstance);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_Init_PostProcessBuffer(const char* BufferID,
int32_t* clientInstance,
int32_t* connectionInstance);

/*--------------------------------------------------------------------------------------*/
/************		Get info about PostProcess buffer
Returns basic information about one post process buffer

IN:
bufferIndex			...	buffer index
bufferIDLen			... maximum length of destination buffer for bufferID
bufferNameLen		... maximum length of destination buffer for bufferName

OUT:
bufferID			... unique buffer id (needed to connect to it)
bufferName			... friendly buffer name

RETURN:
General return codes

ATTENTION:
GetPostProcessBufferCount has to be called before!!
Not thread save! This means that a call to GetPostProcessBufferCount() from another Thread
could change buffer enumeration while reading single buffers!
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_GetPostProcessBufferInfo(uint32_t 	bufferIndex,
char* 		bufferID,
size_t 	bufferIDLen,
char* 		bufferName,
size_t 	bufferNameLen);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_GetPostProcessBufferInfo(uint32_t 	bufferIndex,
char* 		bufferID,
size_t 	bufferIDLen,
char* 		bufferName,
size_t 	bufferNameLen);


/*--------------------------------------------------------------------------------------*/
/************	GetTimeRange

	Returns the first and the last available time stamp of a buffered data source.

	IN:
		connection Instance	...	to select the correct connection
		clientInstance		... to select the correct client

	Out:
		startTimeDC			... uint64_t pointer to the start time variable
		startTimeDC			... uint64_t pointer to the end time variable

	RETURN:
		General return codes

	ATTENTION:
		This function can only be used with PostProcessBuffer or file connections!!

*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_GetTimeRange(int32_t 	connectionInstance,
																 int32_t 	clientInstance,
															     uint64_t* 	startTimeDC,
																 uint64_t* 	endTimeDC);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_GetTimeRange(int32_t 	connectionInstance,
																int32_t 	clientInstance,
																uint64_t* 	startTimeDC,
																uint64_t* 	endTimeDC);

/*--------------------------------------------------------------------------------------*/
/************	Set BackTime

	Is used to set a BackTime manually for the next data request.
	Backtime defines how many seconds of historical data should be read at one request.
	Usually this functionality is used to limit the amount of historical data when starting a connection.

	IN:
		connectionInstance	...	to select the correct connection
		backTimeSec			... >0 : complete buffer will be read
								<=0: the next request will contain the last "BackTime" seconds
									 or the complete buffer if less than "BackTime" seconds 
									 are stored

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_SetBackTime(int32_t connectionInstance,
															    double 	backTimeSec);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_SetBackTime(int32_t 	connectionInstance,
														       double 	backTimeSec);

/*--------------------------------------------------------------------------------------*/
/************	Seek Timestamp

	Moves the current frame pointer to a frame with the given timestamp.

	IN:
		connectionInstance	...	to select the correct connection
		clientInstance		... to select the correct client
		timestamp			... destination timestamp

	RETURN:
		General return codes

	ATTENTION:
		This function can only be used with PostProcessBuffer or file connections!!
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_SeekTimeStamp(int32_t 	connectionInstance,
																  int32_t 	clientInstance,
																  uint64_t 	timestamp);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_SeekTimeStamp(int32_t 	connectionInstance,
																 int32_t 	clientInstance,
															     uint64_t 	timestamp);
/*--------------------------------------------------------------------------------------*/
/************	Seek

	Moves the current frame pointer forward.

	IN:
		connectionInstance	...	to select the correct connection
		clientInstance		... to select the correct client
		seekFrames			... number of frames to seek forward

	RETURN:
		General return codes

	ATTENTION:
		This function can only be used with PostProcessBuffer or file connections!!
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_Seek(int32_t connectionInstance,
														 int32_t clientInstance,
														 size_t  seekFrames);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_Seek(int32_t	connectionInstance,
														int32_t clientInstance,
														size_t	seekFrames);
/*--------------------------------------------------------------------------------------*/
/************	Rewind

	Moves the current frame pointer back.

	IN:
		connectionInstance	...	to select the correct connection
		clientInstance		... to select the correct client
		rewindFrames		... number of frames to rewind

	RETURN:
		General return codes

	ATTENTION:
		This function can only be used with PostProcessBuffer or file connections!!
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_Rewind(int32_t 	connectionInstance,
														   int32_t 	clientInstance,
														   size_t 	rewindFrames);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_Rewind(int32_t 	connectionInstance,
														  int32_t 	clientInstance,
														  size_t 	rewindFrames);
/*--------------------------------------------------------------------------------------*/
/************	Clear Buffer Frames

	Same as "eGateHighSpeedPort_SetBackTime"

*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD 
_CD_eGateHighSpeedPort_ReadBuffer_Clear(int32_t ConnectionInstance,
										double timeLeft);

EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC
SC_eGateHighSpeedPort_ReadBuffer_Clear(int32_t ConnectionInstance,
										double timeLeft);
/*--------------------------------------------------------------------------------------*/
/************		Get Buffer Frames																								

	Returns the number of available (read and decoded) data frames.
	The dll contains a FIFO with a fixed length -> data has to be read out continously
	with all clients, otherwise the data transfer will be paused 
	and the circle buffer may overun!

	IN:
		connectionInstance	...	to select the correct connection
		clientInstance		... to select the correct client
	
	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD 
_CD_eGateHighSpeedPort_GetBufferFrames(int32_t ConnectionInstance,
									   int32_t ClientInstance);

EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC
SC_eGateHighSpeedPort_GetBufferFrames(int32_t ConnectionInstance,
									  int32_t ClientInstance);
/*--------------------------------------------------------------------------------------*/
/************		Get Buffer Frames All

Returns the number of all data frames of the datasource.


IN:
connectionInstance	...	to select the correct connection
clientInstance		... to select the correct client

RETURN:
number of total frames in selected datasource
*/
EGATEHIGHSPEEDPORT_API
int64_t CALLINGCONVENTION_CD
_CD_eGateHighSpeedPort_GetBufferFrames_All(int32_t ConnectionInstance,
											int32_t ClientInstance);

EGATEHIGHSPEEDPORT_API
int64_t CALLINGCONVENTION_SC
SC_eGateHighSpeedPort_GetBufferFrames_All(int32_t ConnectionInstance,
											int32_t ClientInstance);
/*--------------------------------------------------------------------------------------*/
/************		Load Buffer Data

	Returns the number of available (read and decoded) data frames.
	The dll contains a FIFO with a fixed length -> data has to be read out continously
	with all clients, otherwise the data transfer will be paused
	and the circle buffer may overun!

	IN:
		connectionInstance	...	to select the correct connection
		clientInstance		... to select the correct client

	Out:
		frames				... number of available data frames

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD
_CD_eGateHighSpeedPort_LoadBufferData(int32_t connectionInstance, uint32_t *frames);

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC
SC_eGateHighSpeedPort_LoadBufferData(int32_t connectionInstance, uint32_t *frames);
/*--------------------------------------------------------------------------------------*/
/************		Next Frame														

	Used to step to the next frame.
	As long as this function isn't called for all clients,
	"eGateHighSpeedPort_ReadBuffer_Single" will not point to the next frame.

	IN:
		connectionInstance	...	to select the correct connection
		clientInstance		... to select the correct client

	RETURN:
  	  General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD 
_CD_eGateHighSpeedPort_ReadBuffer_NextFrame(int32_t ConnectionInstance,
												 int32_t clientInstance);

EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC
SC_eGateHighSpeedPort_ReadBuffer_NextFrame(int32_t ConnectionInstance,
												 int32_t clientInstance);

#define _CD_eGateHighSpeedPort_ReadBuffer_NextChannel _CD_eGateHighSpeedPort_ReadBuffer_NextFrame
#define SC_eGateHighSpeedPort_ReadBuffer_NextChannel SC_eGateHighSpeedPort_ReadBuffer_NextFrame
/*--------------------------------------------------------------------------------------*/
/************		Read buffered single channel - convert to double										

	Used to read the value of a specified channel from the actual frame and converts it to double.

	IN:
		connectionInstance	...	to select the correct connection
		clientInstance		... to select the correct client
		channel index		... to select the channel index (total index)
								use "eGateHighSpeedPort_GetChannelInfo_int" to convert
								channel index if necessary.

	OUT:
		value				... value converted to double

	RETURN:
		General return codes
*/

EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD 
_CD_eGateHighSpeedPort_ReadBuffer_Single(int32_t ConnectionInstance,
										 int32_t clientInstance,
									     uint32_t ChannelIndex,
										 double* value);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC 
SC_eGateHighSpeedPort_ReadBuffer_Single(int32_t ConnectionInstance,
										int32_t clientInstance,
									    uint32_t ChannelIndex,
										double* value);

/*--------------------------------------------------------------------------------------*/
/************		Read buffered single channel - raw data type

	Used to read the value of a specified channel from the actual frame to buffer.

	IN:
		connectionInstance	...	to select the correct connection
		clientInstance		... to select the correct client
		channel index		... to select the channel index (total index)
								use "eGateHighSpeedPort_GetChannelInfo_int" to convert
								channel index if necessary.

	OUT:
		value				... raw value

	RETURN:
		General return codes
*/

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_ReadBuffer_Single_RawType(int32_t ConnectionInstance,
																			  int32_t clientInstance,
																			  uint32_t ChannelIndex,
																			  char* value,
																			  size_t valueSize);

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_ReadBuffer_Single_RawType(int32_t ConnectionInstance,
																			 int32_t clientInstance,
																			 uint32_t ChannelIndex,
																			 char* value,
																			 size_t valueSize);
/*--------------------------------------------------------------------------------------*/
/************		Read buffered multiple channels										

	Not supported

*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD 
_CD_eGateHighSpeedPort_ReadBuffer_Window(int32_t connectionInstance);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC 
SC_eGateHighSpeedPort_ReadBuffer_Window(int32_t clientInstance);

/*--------------------------------------------------------------------------------------*/
/************		Read buffer to double array									

	Reads buffered data to a double array.
	No worker threads are needed, every call initiates TCP/IP communication and data decoding.

	"eGateHighSpeedPort_Init" and "eGateHighSpeedPort_InitBuffer" has to be used first!

  	IN:
		connectionInstance	...	To select the correct connection
		arrayLength			... Number of elements in "valueArray"
								If "valueArray" is smaller than "arrayLength" this will cause a segfault!!!
		fillArray			... With fillArray set to "1" this call will block until "arrayLength/channelCount"
								frames are received!

	OUT:
		valueArray			... Point32_ter to a double array with at least "ArrayLength" elements
								Contains double converted values.
		receivedFrames		... Number of frames in valueArray after processing
								(frame = 1 sample over all channels)
		channelCount		... Number of channels in one frame
								(can also be read with "getNumberOfChannels")
		complete			...	Indicates if one TCP/IP request was completely decoded


	RETURN:
	General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD 
_CD_eGateHighSpeedPort_ReadBufferToDoubleArray(int32_t ConnectionInstance,
											double *valueArray,
											uint32_t arrayLength,
											uint32_t fillArray,
											uint32_t *receivedFrames,
											uint32_t *channelCount,
											uint32_t *complete);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC 
SC_eGateHighSpeedPort_ReadBufferToDoubleArray(int32_t ConnectionInstance,
											double *valueArray,
											uint32_t arrayLength,
											uint32_t fillArray,
											uint32_t *receivedFrames,
											uint32_t	*channelCount,
											uint32_t *complete);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD 
_CD_eGateHighSpeedPort_ReadBufferToDoubleArray_StraightTimestamp(int32_t ConnectionInstance,
																double *valueArray,
																uint32_t arrayLength,
																uint32_t fillArray,
																uint32_t *receivedFrames,
																uint32_t	*channelCount,
																uint32_t *complete);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC 
SC_eGateHighSpeedPort_ReadBufferToDoubleArray_StraightTimestamp(int32_t ConnectionInstance,
																double *valueArray,
																uint32_t arrayLength,
																uint32_t fillArray,
																uint32_t *receivedFrames,
																uint32_t	*channelCount,
																uint32_t *complete);



/*--------------------------------------------------------------------------------------*/
/************		Log to UDBF-File

TBD -> not completely implemented yet.
used for testing reasons...

IN:
connectionInstance	...	to select the correct connection

RETURN:
1 ....  error
0 ....	no error
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_LogToUDBF_File(	int32_t connectionInstance, 
																	uint64_t framecount, 
																	const char* variableIDs, 
																	const char* fullFileName);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_LogToUDBF_File(	int32_t connectionInstance, 
																	uint64_t framecount, 
																	const char* variableIDs, 
																	const char* fullFileName);



//////////////////////////////////////////////////////////////////////////////////////////
/*------------- DLL Diagnostic ---------------------------------------------------------*/
/*																						*/
/*	Description:																		*/
/*																						*/
/*		Following functions provide diagnostic actions and information's				*/
/*																						*/
//////////////////////////////////////////////////////////////////////////////////////////	
/*--------------------------------------------------------------------------------------*/
/************		DLL Version/Date													*/
EGATEHIGHSPEEDPORT_API 
void CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_IdentDLL(char *dllVersion, 
												          char *dllDate);
EGATEHIGHSPEEDPORT_API 
void CALLINGCONVENTION_SC SC_eGateHighSpeedPort_IdentDLL(char *dllVersion, 
														 char *dllDate);
/*--------------------------------------------------------------------------------------*/
/************		Toggle debug mode													

	In debug mode, this DLL will generate a log file.

*/
EGATEHIGHSPEEDPORT_API 
void CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_ToggleDebugMode(void);
EGATEHIGHSPEEDPORT_API 
void CALLINGCONVENTION_SC SC_eGateHighSpeedPort_ToggleDebugMode(void);
/*--------------------------------------------------------------------------------------*/
/************		Explain error message												

	Is used to get error information in plain text if any error-returncode is thrown

	IN:
		connectionInstance	...	to select the correct connection

	OUT:
		error message		... plain text error message

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_ExplainError(int32_t connectionInstance, 
															 char errorMessage[]);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_ExplainError(int32_t connectionInstance, 
															char errorMessage[]);

/*--------------------------------------------------------------------------------------*/
/************		Get debug message												

	Is used to get error information in plain text if any error-returncode is thrown

	IN:
		connectionInstance	...	to select the correct connection

	OUT:
		debug message		... plain text error message

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_GetDebugMessage(char errorMessage[]);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_GetDebugMessage(char errorMessage[]);

/*--------------------------------------------------------------------------------------*/
/************		Get debug message	*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_WriteDebugMessage(char errorMessage[]);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_WriteDebugMessage(char errorMessage[]);
/*--------------------------------------------------------------------------------------*/
/************		Read Connection State										
																					
	If a connection is broken (e.g. ethernet disconnect or module restart) the dll 
	will try to establish the connection agin as int32_t as the connection isn't terminated.

	This function can be used to indicate the actual connection state.
	
	IN:
		connectionInstance	...	to select the correct connection

	RETURN:
		1 ....  connection open
		0 ....	connection closed
*/
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_Connected(int32_t connectionInstance);
EGATEHIGHSPEEDPORT_API 
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_Connected(int32_t connectionInstance);
/*--------------------------------------------------------------------------------------*/
/************		Get Diagnostic														


	Provides system diagnostic info's
	
	Diag info's are only up to date when diagLevel==DIAG_CONTROLLER was used before!
	If errorCount != 0 then other diagLevels can be checked for errors.

	IN:
		connectionInstance	...	to select the correct connection
		diagLevel			... to request the desired info
		index				... request the info from a specified index

	OUT:	
		cycleCount			... number of communication cycles for the requested item (should be)
		errorCount			... diagLevel==DIAG_CONTROLLER:
									the number of errors over the whole system.
									Use this diagLevel to refresh diag data!
								diagLevel==DIAG_int32_tERFACE:
									the number of error on a specifc int32_terface
									(int32_ternal, UART1, UART2,...)
								diagLevel==DIAG_TRANSPORT:
									the number of error on a specifc transport
									(system variables, virtual variables, Slave1, Slave2,..)
								diagLevel==DIAG_VARIABLE:
									not used
								diagLevel==DIAG_ITEMCOUNT:
									the number of items for the defined level

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_Diagnostic(int32_t ConnectionInstance,
														   uint32_t diagLevel,
														   uint32_t index,
														   uint32_t *cycleCount,
														   uint32_t *errorCount);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_Diagnostic(int32_t ConnectionInstance,
														  uint32_t diagLevel,
														  uint32_t index,
														  uint32_t *state,
														  uint32_t *errorCount);

/*--------------------------------------------------------------------------------------*/
/************		Remote control command												

	This function is part of the inter process communication mechanism.

	It can be used to send commands to every process that uses the DLL
*/
EGATEHIGHSPEEDPORT_API
void CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_RemoteControl(int32_t controlID);

EGATEHIGHSPEEDPORT_API
void CALLINGCONVENTION_SC SC_eGateHighSpeedPort_RemoteControl(int32_t controlID);
//////////////////////////////////////////////////////////////////////////////////////////
/*------------- File transfer functions ------------------------------------------------*/
/*																						*/
/*	Description:																		*/
/*																						*/
/*		Following functions provide file transfer - and decode functions				*/
/*																						*/
/*		Files can only be read or deleted completely, but not written or modified.		*/
/*		Configuration handling has to be done via FTP									*/
/*																						*/ 
/*		Files can either be copied to a drive or decoded online without storing to a	*/
/*		file.																			*/
/*		After decoding data from local files or a file stream from the controller,		*/	
/*		the values are accessible in the same way as reading buffer values.				*/																
/*		(eGateHighSpeedPort_ReadBuffer_NextFrame, eGateHighSpeedPort_ReadBuffer_Single)	*/
/*																						*/
//////////////////////////////////////////////////////////////////////////////////////////	
/*--------------------------------------------------------------------------------------*/
/************		Number of files														

	Used to read the number of files on the device.
	A file TypeID is also neccessary to control the desired file type

	This function will also store file specific info's which can be read with
	"eGateHighSpeedPort_GetFileInfo".

	IN:
		connectionInstance	... to select the correct connection
		fileTypeID			... to define the file type on e.gate, Q.gate, Q.pac 
								(use FILE_DIR_ALL to get all Files or 
								FILE_IDENTIFY_BY_PATH to specify a sub path on e.g. Q.Station)
		filePath			... sub path on the device

	OUT:
		fileCount			... number of files regarding file type

	RETURN:
	General return codes
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_GetFileCount(int32_t ConnectionInstance, 
																uint32_t	 fileTypeID,
																const char  *filePath,
																uint32_t*	 fileCount);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_GetFileCount(int32_t ConnectionInstance, 
																uint32_t	fileTypeID,
																const char  *filePath,
																uint32_t*	fileCount);
/*--------------------------------------------------------------------------------------*/
/************		Get file info														

	Used to read name, size and time of a specified file.

	IN:
		connectionInstance	... to select the correct connection
		fileIndex			... index to select a certain file

	OUT:
		fileName			... fileName on device
		fileNameLen			... capacity of fileName buffer
		fileIdent			... file identification, needed to access file on device
		fileIdentLen		... capacity of fileIdent buffer
		size				... size of file
		OLETime				...	days since 01.01.1900 00:00:00
								(use eGate_OLETime2TimeStruct to convert)
								ATTENTION: 
								this time is not absolutely synchronous to the timestamp!
								
	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_GetFileInfo(int32_t ConnectionInstance, 
																uint32_t fileIndex,
																char *fileName,
																uint32_t fileNameLen,
																char* fileIdent,
																uint32_t fileIdentLen,
																uint32_t* size,
																double* OLETime);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_GetFileInfo(int32_t ConnectionInstance, 
															   uint32_t fileIndex,
															   char *fileName,
															   uint32_t fileNameLen,
															   char* fileIdent,
															   uint32_t fileIdentLen,
														       uint32_t *size,
														       double *OLETime);
/*--------------------------------------------------------------------------------------*/
/************		Copy file															

	Used to copy a file on device to a local path

	IN:
		connectionInstance	... to select the correct connection
		fileIdent			... file identification as received with "_CD_eGateHighSpeedPort_GetFileInfo()"
		savePath			... existing path + file name

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_CopyFile(int32_t ConnectionInstance, 
														 const char *fileIdent,
														 const char *savePath);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_CopyFile(int32_t ConnectionInstance, 
														const char *fileIdent,
														const char *savePath);
/*--------------------------------------------------------------------------------------*/
/************		Delete file															

	Used to delete a file on device

	IN:
		connectionInstance	... to select the correct connection
		fileIdent			... file identification as received with "_CD_eGateHighSpeedPort_GetFileInfo()"

	RETURN:
		General return codes
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_DeleteFile(int32_t ConnectionInstance, 
														   const char *fileIdent);
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_DeleteFile(int32_t ConnectionInstance, 
														  const char *fileIdent);

/*--------------------------------------------------------------------------------------*/
/************		Read and decode file
This function initializes any UDBF file as it was a connection.
Common buffer functions can be used to access the data

IN:
fileName			...	source file name

OUT:
client Instance		... If several tasks of the application uses the same connection,
some DLL functions need the client instance for synchronisation.
connectionInstance	... handle that identifies/selects a connection

RETURN:
General return codes
*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_DecodeFile_Select(int32_t* clientInstance,
int32_t* connectionInstance,
const char* fileName);

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_DecodeFile_Select(int32_t* clientInstance,
int32_t* connectionInstance,
const char* fileName);

/*------------- Helper -------------------------------------------------------*/
EGATEHIGHSPEEDPORT_API 
double CALLINGCONVENTION_CD _CD_eGate_TimeStruct2OLETime(int32_t year, 
														 int32_t month, 
														 int32_t day, 
														 int32_t hour, 
														 int32_t minute,
														 int32_t second, 
														 double belowSeconds);
EGATEHIGHSPEEDPORT_API 
double CALLINGCONVENTION_CD _SC_eGate_TimeStruct2OLETime(int32_t year, 
														int32_t month, 
														int32_t day, 
														int32_t hour, 
														int32_t minute,
														int32_t second, 
														double belowSeconds);
EGATEHIGHSPEEDPORT_API 
double CALLINGCONVENTION_CD _CD_eGate_OLETime2TimeStruct(double OLETime,
														 int32_t *year, 
														 int32_t *month, 
														 int32_t *day, 
														 int32_t *hour, 
														 int32_t *minute,
														 int32_t *second, 
														 double *belowSeconds);
EGATEHIGHSPEEDPORT_API 
double CALLINGCONVENTION_CD _SC_eGate_OLETime2TimeStruct(double OLETime,
														int32_t *year, 
														int32_t *month, 
														int32_t *day, 
														int32_t *hour, 
														int32_t *minute,
														int32_t *second, 
														double *belowSeconds);

/*--------------------------------------------------------------------------------------*/
/************		Sleep MS											

	Can be used to sleep

	IN:
		time_msec			 ... time to sleep in milli seconds

	RETURN:
		General return codes

*/
EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_CD _CD_eGateHighSpeedPort_SleepMS(int32_t time_msec);

EGATEHIGHSPEEDPORT_API
int32_t CALLINGCONVENTION_SC SC_eGateHighSpeedPort_SleepMS(int32_t time_msec);



#ifdef __cplusplus
}
#endif


