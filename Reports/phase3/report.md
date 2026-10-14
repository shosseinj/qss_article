# گزارش واقعی Phase 3 — ۱۴ اکتبر ۲۰۲۶

**آماده‌سازی نرم‌افزار انجام شد؛ Phase 3 تجربی کامل نشده است.** کاربر تأیید کرد checkpointها و دادهٔ N-MNIST در این سیستم موجود نیستند و کارهای وابسته باید برای آینده بمانند. تعداد آزمایش‌های واقعی تکمیل‌شده **صفر** است؛ clean/attack test، اختلاف selection، زمان campaign و ETA نامعلوم‌اند و در JSONها `null` ثبت شده‌اند.

## آنچه انجام شد

- فایل‌ها و گزارش‌های Phase 2 دوباره بررسی شدند. baseline عددی/ارجاع‌ها پاس شد؛ داده‌های تاریخی و حذف قبلی `guide.md` حفظ شدند.
- موجودی **۷۰ مدخل** از فایل‌های موجود و artifactهای مورد انتظار تهیه شد. هیچ checkpoint، dataset خام، manifest اجرایی یا trajectory واقعی در پروژه/بسته‌های Overleaf یافت نشد.
- درخت عمومی GitHub با **۶۰۱ مدخل و بدون truncation** در commit تاریخی بررسی شد. **۲۶ فایل سورس** مفقود، شامل loader canonical و تعریف مدل‌ها، بازیابی و Git blob/SHA-256 آن‌ها تأیید شد. این بازیابی، بازیابی وزن یا داده نیست. کد baselineهای grid اکنون در پوشهٔ recovery موجود است؛ checkpoint/config اجرای آن‌ها همچنان موجود نیست و ممیزی اجرایی grid انجام نشده است.
- یک محیط **CPU برای آزمون** با Python 3.12، PyTorch 2.5.1+cpu و NumPy 1.26.4 در `/tmp/qsnn-phase3-venv` ساخته شد. CUDA/GPU در دسترس نیست. نسخه‌های تاریخی متفاوتِ requirements و یادداشت محیط به‌عنوان ابهام حفظ شدند؛ محیط تازه معادل قطعی همهٔ اجراهای گذشته معرفی نشده است.
- runner جدید در `scripts/phase3/` ایجاد شد. سورس PGD/TEMP تاریخی دست‌کاری نشده است. runner از checkpoint با hash/metadata/state_dict صحیح و NPZ واقعی با ID/x/y/p/t/label استفاده می‌کند؛ فایل مفقود را با داده یا وزن تصادفی جایگزین نمی‌کند.
- PGD با CE/margin، clean start و restartهای اضافی، و TEMP با scheduleهای literal و تعداد واقعی proposals پیاده شدند. callهای batched، forward-equivalent، backward، verification و هزینهٔ تحلیل جدا ثبت می‌شوند. TEMP فقط margin را می‌پذیرد.
- maximum-loss/margin selection و success-priority از **همان بانک logits تأییدشده و همان candidateها** محاسبه می‌شوند. خروجی منتخب حین search و تغییر selection هنگام reevaluation جدا ثبت می‌شود؛ تغییر غیرمنتظرهٔ argmax در audit اجرای مثال را نامعتبر می‌کند.
- validity خام، fallback تمیز، argmax tie، best-so-far، مخرجِ ثابت، عدم تبدیل missing/failed به survivor، ذخیرهٔ atomic و resume با config/source/environment fingerprint پیاده شدند. source fingerprint لازم است چون HEAD محلی پیش از تغییرهای uncommitted Phase 2/3 است.
- constructorهای Q کامل، classical nonlinear head و Q بدون entangler، خروجی statevector و بررسی TV/trace-distance/margin آماده شدند. **این constructorها، training یا ablation انجام‌شده نیستند.** training campaign، sweep خودکار، calibration خودکار و تولید manifest از dataset اصلی هنوز باید همراه artifactهای واقعی تکمیل شوند.
- config توسعه، pilot، test، ablation و preregistration داخلی آماده‌اند. preregistration عمداً **draft** است؛ hyperparameter نهایی از نتیجهٔ غیرموجود انتخاب نشده و test باز نشده است.

## آزمون و محدودیت آن

**۲۸ آزمون پاس شدند**؛ شامل CE counterexample، اعتبار eventها، tie صفر-margin، بودجه و تعداد call، adapter canonical بازیابی‌شده، reset/eval و جابه‌جایی batch، مشتق گیت differentiable، همزیستی surrogate غیرصفر با hard-forward ثابت، state export، جلوگیری از مخرج ناقص و resume/provenance.

آزمون‌های integration از فایل‌های checkpoint مصنوعی و مدل بدون آموزش **فقط داخل پوشهٔ موقت آزمون** استفاده کردند و آن‌ها را حذف کردند. این‌ها pilot مدل واقعی، replay تاریخی، اثبات اختلاف ASR یا ارزیابی QSNN نیستند. زمان unit test برای ETA استفاده نشد.

یک بازبینی مستقل سورس سه ایراد مهم در objective TEMP، مشترک‌بودن logits انتخاب و provenance محیط resume پیدا کرد. هر سه با آزمون failing→passing و اجرای کامل suite اصلاح شدند. ثبت provenance خروجی clean-evaluation نیز با آزمون integration بررسی شد. [گزارش بازبینی](review.txt) و [لاگ آزمون](unit-tests.log) محفوظ‌اند.

فرمان واقعی pilot اجرا شد و در **بررسی پیش‌نیازها** با `blocked_resource` متوقف شد: checkpoint/metadata/manifest و hashهایشان موجود نیستند. هیچ forward واقعی با مدل آموزش‌دیده انجام نشد و خروجی علمی ساخته نشد. [pilot.json](pilot.json) و [selection_audit.json](selection_audit.json) نتیجهٔ اندازه‌گیری‌نشده را صفر گزارش نمی‌کنند.

## مقاله و شکل‌ها

فقط اصلاح‌های کوچک بخش ۸ اعمال شد: فونت گیت‌ها از ۶٫۷ به ۸pt افزایش یافت؛ کلید `Cand./fwd.` صریح شد؛ paired overlap به جدول شمارش چهارگروهی تبدیل شد تا اختلاف ۱–۲ مثالی زیر Neither گم نشود. کپشن تأکید می‌کند برابری aggregate counts هویت یکسان نمونه‌ها بین دو شرط را اثبات نمی‌کند. شکل grid بررسی شد و نیاز به تغییر تازه نداشت.

اعداد Results، منابع و ادعاهای تجربی قبلی تغییر نکردند و نتیجهٔ تازه‌ای به Abstract/Conclusion افزوده نشد. main و supplement کامپایل شدند: **۸ و ۱۷ صفحه**. صفحات ۳ و ۶ main بصری بررسی شدند؛ logها بدون undefined citation/reference، duplicate label و Overfull box هستند. build موفق تأیید تجربی محسوب نمی‌شود.

## ادامهٔ کار و فایل‌ها

ترتیب ادامه در [فهرست کارهای آینده](future-work.md) ثبت شده است: artifact واقعی → P0 pilot → selection audit → validation tuning و calibration → قفل پروتکل → official test → pipelineهای مستقل → ablation → exemplar/state–margin واقعی.

- [وضعیت هر مورد](execution_status.json): ۴ مورد تکمیل نرم‌افزاری/مستندی، ۲ مورد implemented و ۸ مسیر اندازه‌گیری وابسته به منابع، منتقل‌شده به آینده؛ **۰ آزمایش واقعی completed**.
- [موجودی](inventory.json)، [محیط](environment.json)، [سورس بازیابی‌شده](recovered-source.json)، [کنترل نهایی](verification.json).
- راه‌اندازی و schema: [scripts/phase3/README.md](../../scripts/phase3/README.md).
- configها: `configs/phase3/`؛ سورس بازیابی‌شده: `results/phase3/recovery/source/`؛ آزمون‌ها: `tests/phase3/`.
- شکل‌های اصلاح‌شده و source آن‌ها، `sections/results.tex`، README و ignore فایل‌های بزرگ به‌روز شدند؛ جدول‌ها و raw data تاریخی تغییر نکردند.

HEAD محلی: `2cc6be05f346b65f8716967df3bff2461d1a6298`. snapshot تاریخی: `80d02f5733d4cbe7c3e69b828dff66d50ba5c211`. hash کد فعلی جدا در inventory/run provenance ثبت می‌شود. **هیچ commit، push یا آپلود Overleaf انجام نشد.**
