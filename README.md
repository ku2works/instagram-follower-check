conda upgrade -y --all
conda clean -y --packages

python -m pip install --upgrade pip
conda activate py37
conda deactivate

# 本番環境用
pip install --requirement ./conf/requirements.txt --target ./src/vendor

# ローカル環境用
pip install --requirement ./conf/requirements-dev.txt

pip freeze | Out-File -Encoding UTF8 .\requirements.txt