echo " BUILD START"

python3.9  -m pip install -r requirements.txt
python3.9 manage.py collectstatic  --noinput --clear
mkdir static
echo " BUILD END"
ls
echo "test"
cd read
ls