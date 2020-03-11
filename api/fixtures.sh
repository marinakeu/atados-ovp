echo "Core: "
python manage.py loaddata addresstypes components address posts

echo "Images: "
python manage.py loaddata images

echo "Users: "
python manage.py loaddata users profiles

echo "Organizations: "
python manage.py loaddata organizations

echo "Project: "
python manage.py loaddata projects roles works jobs jobdates applies categories projectbookmarks

echo "Catalogue: "
python manage.py loaddata catalogue

# Donations
# TODO: Subscription (finish subscriptions on donations app first)
echo "Donations: "
python manage.py loaddata sellers transactions

# Faq
echo "FAQ: "
python manage.py loaddata faqcategory faq
