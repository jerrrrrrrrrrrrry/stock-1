if "%1"=="hide" goto CmdBegin
start mshta vbscript:createobject("wscript.shell").run("""%~0"" hide",0)(window.close)&&exit
:CmdBegin
python .\beta_0.py
python .\beta_2.py
python .\beta_4.py
python .\betacov_0.py