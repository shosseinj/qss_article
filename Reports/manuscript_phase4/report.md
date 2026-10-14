# گزارش اجرای Manuscript Phase 4 — ۱۴ اکتبر ۲۰۲۶

اصلاح‌های ویرایشی، منابع، ممیزی ایستای کد و خروجی PDF انجام شد. **اعتبارسنجی تجربی فاز کامل نیست: تعداد آزمایش واقعی جدید صفر است.** مطابق تصمیم قبلی کاربر، کارهای وابسته به داده و checkpoint که در این سیستم موجود نیستند برای آینده ثبت شدند.

## خروجی‌ها

- [مقالهٔ ۹صفحه‌ای](../../build/main.pdf) و [supplement هجده‌صفحه‌ای](../../build/supplement.pdf).
- [پاسخ تک‌تک R1–R8 و M1–M13](response_to_review.md)، همراه فایل تغییر، شاهد، وضعیت و محدودیت؛ نسخهٔ ماشینی در response_to_review.csv.
- [تأیید ماشینی](verification.json)، [تست‌ها](unit-tests.log)، [بررسی بصری](visual_review.md)، [diff متن و کد](source.diff).
- [دفتر ادعا–شاهد](claim_evidence.csv)، [دفتر منابع](citation_ledger.csv)، [جدول هزینه](compute_accounting.csv)، [ماتریس موجودبودن artifacts](repository_availability.json).

۱۵ مورد resolved، چهار مورد partially_resolved و دو مورد blocked است. R1 و R2 به‌علت نبود داده/وزن مسدودند؛ R3، R6، R7 و R8 فقط در بخش‌های قابل بررسی پیش رفته‌اند. همهٔ جزئیات در پاسخ داوری و [کارهای باقی‌مانده](remaining_work.md) آمده است.

## یافته‌های ممیزی و اصلاح مقاله

۱. loader و تعریف baselineها، اسکریپت آموزش و حمله موجودند. عبارت‌های قدیمی دربارهٔ نبود کلی تعریف baseline حذف شد؛ source از config نهایی، وزن و اتصال به اجرای تاریخی تفکیک شد. هفت فایل دیگر از commit ثابت مخزن بازیابی و با Git blob hash بررسی شد. چهار فایل upstream بازیابی شد؛ سه تعریف مدل مرجع با فایل‌های local دقیقاً یکسان‌اند. manifest کامل شامل ۳۷ فایل بازیابی‌شدهٔ دو فاز است.

۲. ConvNet همان **spiking SimpleNet_v2** است؛ کلاس ReLU جداگانه انتخاب نشده است. جدول مدل‌ها class، spiking بودن، تجمیع زمانی، شمارش پارامتر قابل تأیید و source hash را روشن می‌کند. شمارش مرجعِ مقاله جای پارامترهای checkpoint محلی ننشست. سازندهٔ custom SNN بدون وزن آموزش‌دیده ۲۵٬۴۸۲ پارامتر دارد؛ رفتار checkpoint تاریخی تأیید نشده است.

۳. در training source، با وجود انتخاب checkpoint بر اساس validation، skip/status/revise به test accuracy با آستانهٔ ۰٫۹۵ وابسته است. این ریسک در مقاله و [test-access audit](test_access_audit.md) افشا شد؛ بدون chronology نمی‌توان وقوع تغییر recipe یا استقلال test را نتیجه گرفت. utility تازهٔ completion/resume از test accuracy استفاده نمی‌کند و gateهای validity، جدایی split، freeze روی validation و hashها را حفظ می‌کند. شش تست آن پاس است. **ادغام این policy در runner کامل آموزش و اجرای آن هنوز انجام نشده**؛ سورس تاریخی دست‌نخورده ماند.

۴. فایل upstream دقیقِ B0 با SHA-256 مورد انتظار adapter بازیابی شد. loss ضریب ثابت **۵** برای جریمهٔ عبور از بودجه دارد؛ `lambda_cap=20` جریمهٔ ظرفیت است و `lambda_B=0` آن ضریب ثابت را تعیین نمی‌کند. config سطح سورس و call flags ثبت شدند. runtime واقعی هر اجرای تاریخی و پیوند artifacts همچنان نامعلوم است.

۵. cost table اکنون candidate، model invocation، مجموع batch size، backward و verification را جدا می‌کند. تعداد callهای TEMP در چهار schedule گزارش‌شده به‌ترتیب ۵، ۵، ۶۴ و ۲۶ از سورس استنباط می‌شود؛ این‌ها counter اندازه‌گیری‌شده نیستند. warm-up درخواست ۴۰۰، عملاً ۳۹۸ proposal می‌سازد. unique candidateها و زمان خام تاریخی null/ناموجود مانده‌اند؛ سخت‌افزار فعلی جای snapshot زمان اجرا ننشست.

۶. notation رویداد/کلاس/احتمال، فرمول exact McNemar، حدود Wilson، شرط کافیِ readout ثابت، اثر finite search و هزینهٔ cumulative روشن شد. ablation قدیمی ۱۵۴–۲۷۴پارامتری با local Pauli-Z از مدل نهایی ۴۰٬۷۶۲پارامتری جدا شد. داده و نتایج تاریخی تغییر نکرد.

## منابع و PDF

۱۲ منبع پیشنهادی با منابع قبلی ادغام و واقعاً استناد شدند: کتابنامه ۳۲ مدخل یکتا دارد و هر ۳۲ در متن اصلی cite شده‌اند. DOI/title تکراری و citation/reference نامعین وجود ندارد؛ nocite ستاره‌دار حذف شد. metadata جدید از منابع اولیه بررسی و محدودیت بررسی هر مدخل در ledger ثبت شد. DOI و صفحات QCE از Crossref و صفحات CVPR از PDF رسمی تأیید شدند. backend همان BibTeX است؛ style با نام تازه، DOI/URL استاندارد را چاپ می‌کند و از شکستن یک مدخل بین صفحه‌ها جلوگیری می‌شود.

سه شکل در خاکستری و صفحه‌آرایی PDF بررسی شدند؛ شکل ۱ legend تازه دارد و متن تکراری زیر محور شکل ۲ حذف شد. نمودار ۳ همان داده و artwork تاریخی را حفظ می‌کند. PDF/SVG هر سه شکل vector است. مقاله از ۸ به ۹ صفحه رسیده؛ محدودیت venue مشخصی ارائه نشده و فونت برای تحمیل تعداد صفحه کوچک نشد.

## تأیید و حدود پایان

۳۴ تست نرم‌افزاری با صفر failure/error پاس شد؛ این تست‌ها synthetic/untrained هستند. تأیید ماشینی ۱۶ ردیف paired، ۱۶ سلول grid، arithmetic، هزینه‌های ایستا، ۳۲ منبع، buildها، cross-referenceها، vector exportها و hashهای ۱۰۴ فایل حفاظت‌شده را بررسی کرد. data/، گزارش‌های Phase 3 و سورس تاریخی آن بدون تغییرند. خطای build یا overflow وجود ندارد؛ چهار underfull box بی‌اثر در main و یک warning قدیمی amsmath در supplement در گزارش آمده است.

هیچ official-test QSNN، ممیزی selection واقعی، timing calibration، آموزش ablation یا exemplar/state–margin واقعی اجرا نشده است. final-test lock همچنان draft است. هیچ commit، push، ارسال مقاله یا تغییر Overleaf انجام نشده است.

[بازبینی مستقل نهایی](final_review.md) ایراد Critical/Important پیدا نکرد؛ ابهام جزئی نماد کلاس اصلاح و هر دو PDF دوباره build و بررسی شدند.
