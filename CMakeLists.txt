################################################################################
# CMakeLists.txt
#
# Copyright (C) 2024, Gantner Instruments GmbH. All rights reserved.
################################################################################

# Option to control whether dependencies are installed
# This installs the package with its requirements and is necessary for generated documentation
option(GINS_GIMODULES_INSTALL_PYTHON_DEPENDENCIES "Install required Python dependencies" OFF)

if (GINS_GIMODULES_INSTALL_PYTHON_DEPENDENCIES)
    find_package(Python REQUIRED)

    execute_process(
        COMMAND "${Python_EXECUTABLE}" -m pip install -e ${CMAKE_CURRENT_LIST_DIR} --no-deps
        WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    )
endif()