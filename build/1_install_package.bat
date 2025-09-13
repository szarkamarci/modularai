set "PYTHON_VERSION=3.10"
set "DEV_ENV_PATH=.\.conda_dev_env"

if not exist %DEV_ENV_PATH%nul (
	@ECHO Creating new environment %DEV_ENV_PATH%...
	call conda create --prefix %DEV_ENV_PATH% python=%PYTHON_VERSION% -y
	@ECHO Created new environment %DEV_ENV_PATH%.
)

@ECHO Activating new environment %DEV_ENV_PATH%...
call conda config --set env_prompt "({name})"
call conda activate %DEV_ENV_PATH%
@ECHO Activated virtual environment %DEV_ENV_PATH%.

@ECHO Poetry installing...
pip install --upgrade poetry
@ECHO Poetry install completed.

if exist poetry.lock (
	echo poetry lock file was detected. Remove it to update dependencies?
	del poetry.lock /p
)
    
@ECHO Installing develop, main packages...
call poetry install --no-interaction --with dev,main
@ECHO Installed develop, main packages.

@ECHO Creating subfolders...
REM default directories
CD ..
set dir_list="src" "db" "docs" "dist" "test" "logs" "scripts" "tmp"

(for %%d in (%dir_list%) do (
	if not exist %%d (
		MD %%d
		echo . > %%d\.gitkeep)
))
@ECHO Created subfolders.
@ECHO Finished

PAUSE