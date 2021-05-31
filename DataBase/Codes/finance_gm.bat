if "%1"=="hide" goto CmdBegin
start mshta vbscript:createobject("wscript.shell").run("""%~0"" hide",0)(window.close)&&exit
:CmdBegin
start python .\gm_balance.py
start python .\gm_income.py
start python .\gm_cashflow.py