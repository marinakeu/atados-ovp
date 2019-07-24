echo "Core: "
python manage.py loaddata core.json
echo "Channel: "
python manage.py loaddata channel.json
echo "Users: "
python manage.py loaddata users.json
echo "Organizations: "
python manage.py loaddata organizations.json
echo "Project: "
python manage.py loaddata project.json
echo "VolunteerRole: "
python manage.py loaddata volunteerrole.json
echo "Job: "
python manage.py loaddata job.json
echo "JobDate: "
python manage.py loaddata jobdate.json
echo "Work: "
python manage.py loaddata work.json
echo "Apply: "
python manage.py loaddata apply.json
