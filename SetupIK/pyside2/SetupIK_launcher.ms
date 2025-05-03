current_path = pathConfig.removePathLeaf(getSourceFileName())
python_script_path = current_path + "\\SetupIK_launcher.py"
	
pythonScript = "from SetupIK_launcher import onMaxDroppedPythonFile; onMaxDroppedPythonFile()"

Python.ExecuteFile python_script_path
Python.Execute pythonScript