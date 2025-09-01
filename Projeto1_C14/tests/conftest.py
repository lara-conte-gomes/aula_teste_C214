# Projeto1_C14/tests/conftest.py
import sys, pathlib
# adiciona a pasta do projeto (um nível acima da pasta tests) ao PYTHONPATH
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))