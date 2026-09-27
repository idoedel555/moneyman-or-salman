# הסוכן הפיננסי - בוט טלגרם

בוט שקורא נתונים מהגיליון שה-scraper (moneyman) כותב אליו, ועונה על שאלות פיננסיות דרך Claude.

## שלב 1 - להעלות את הקבצים לריפו
בעמוד הריפו ב-GitHub, ללחוץ על "uploading an existing file" ולגרור את 4 הקבצים: `bot.py`, `requirements.txt`, `.env.example`, `README.md`.
**אל תעלה קובץ עם טוקנים/מפתחות אמיתיים** - `.env.example` הוא רק תבנית.

## שלב 2 - להכין Service Account בגוגל
1. להיכנס ל-Google Cloud Console, ליצור פרויקט (או להשתמש בקיים).
2. להפעיל את Google Sheets API.
3. ליצור Service Account, ולהוריד ממנו קובץ מפתח JSON.
4. לשתף את הגיליון של moneyman עם כתובת המייל של ה-Service Account (viewer/צפייה בלבד).

## שלב 3 - לפרוס ב-Railway (או Render)
1. להירשם עם משתמש GitHub.
2. New Project → Deploy from GitHub repo → לבחור את הריפו הזה.
3. בהגדרות הפרויקט → Variables, להוסיף את כל המשתנים מ-`.env.example` עם הערכים האמיתיים:
   - `TELEGRAM_BOT_TOKEN`
   - `ANTHROPIC_API_KEY`
   - `GOOGLE_SHEET_ID`
   - `GOOGLE_WORKSHEET_NAME`
   - `GOOGLE_CREDENTIALS_JSON` (כל תוכן קובץ ה-JSON, מודבק כמחרוזת אחת)
4. Railway יתקין אוטומטית את מה שב-`requirements.txt` ויריץ `python bot.py`.

## שלב 4 - בדיקה
לפתוח את הבוט בטלגרם, לשלוח `/start`, ואז לשאול שאלה אמיתית כמו "כמה הוצאתי החודש על אוכל?".
