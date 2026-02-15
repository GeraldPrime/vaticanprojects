#!/bin/bash
# Script to check Django error logs on VPS

echo "=== Checking Django Error Logs ==="
echo ""
echo "1. Checking recent Django logs:"
echo "-----------------------------------"
tail -100 /opt/vaticanprojects/vaticanprojects/vaticanprojects/django.log 2>/dev/null | grep -A 20 "500\|Error\|Exception\|Traceback" | tail -200

echo ""
echo "2. Checking Gunicorn logs:"
echo "-----------------------------------"
journalctl -u vaticanprojects -n 50 --no-pager 2>/dev/null | grep -A 20 "500\|Error\|Exception\|Traceback" | tail -200

echo ""
echo "3. Checking if migration has been run:"
echo "-----------------------------------"
cd /opt/vaticanprojects/vaticanprojects/vaticanprojects && python manage.py showmigrations estate | grep 0027

echo ""
echo "4. Checking database for created_by field:"
echo "-----------------------------------"
cd /opt/vaticanprojects/vaticanprojects/vaticanprojects && python manage.py shell -c "from django.db import connection; cursor = connection.cursor(); cursor.execute(\"PRAGMA table_info(estate_propertysale)\"); print('\n'.join([str(row) for row in cursor.fetchall()]))" | grep -i created_by

echo ""
echo "=== Done ==="

