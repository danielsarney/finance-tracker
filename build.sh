set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Only run migrations if DATABASE_URL is set (production)
if [ -n "$DATABASE_URL" ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
else
    echo "Skipping migrations - no DATABASE_URL set"
fi
