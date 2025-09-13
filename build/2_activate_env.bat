@echo off
:: This batch file is used to create and activate a Conda environment.
:: If the environment already exists, the environment is just activated

set "PYTHON_VERSION=3.10"
set "DEV_ENV_PATH=.\.conda_dev_env"

if not exist %DEV_ENV_PATH%nul (
	@ECHO Creating new environment %DEV_ENV_PATH%...
	call conda create --prefix %DEV_ENV_PATH% python=%PYTHON_VERSION% -y
	@ECHO Created new environment %DEV_ENV_PATH%.
)

@ECHO Activating new environment %DEV_ENV_PATH%...
call conda activate %DEV_ENV_PATH%
@ECHO Activated virtual environment %DEV_ENV_PATH%.

CD ../src
START cmd /k