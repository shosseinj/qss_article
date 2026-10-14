# Phase 3 — اعتبارسنجی اجرایی، ارزیابی مستقل و روشن‌کردن نقش مدل هیبرید

**پروژه:** Temporal Retiming Attacks on Hybrid Quantum Spiking Classifiers  
**مبنای برنامه:** نسخهٔ هشت‌صفحه‌ای `main(2).pdf` و گزارش اجرای phase2 مورخ ۱۴ اکتبر ۲۰۲۶  
**نوع فایل:** دستور مرحلهٔ بعد برای Codex در مخزن محلی کاربر؛ این فایل گزارش اجرای آزمایش‌های Phase 3 نیست.

## 0. هدف و نقطهٔ شروع

Phase 2 را از ابتدا تکرار نکن. طبق گزارش اجرا، بازنویسی و بازطراحی شکل‌ها انجام شده‌اند؛ PDF جدید نیز تمرکز بهتر بر QSNN، مدار تفصیلی، ASR با interval و نمایش زوجی دارد. مرحلهٔ بعد باید شواهد اجرایی و نتیجهٔ مستقل تولید کند. افزودن تعداد زیادی رفرنس، تعویض دوبارهٔ رنگ نمودارها و طولانی‌ترکردن متن اولویت این مرحله نیستند.

**پرسش اصلی Phase 3:** آیا نتیجهٔ مقایسهٔ حملات پس از ممیزی selection و افزایش قدرت جست‌وجو، روی دادهٔ test و مدل‌های مستقل نیز برقرار می‌ماند؛ و با کنترل frontend، head کوانتومی چه تفاوتی ایجاد می‌کند؟

گزارش phase2 مدعی build موفق و ممیزی ایستای سورس است. در این برنامه آن‌ها «گزارش‌شده» محسوب می‌شوند؛ بررسی مستقل فایل‌های report، supplement، کد و checkpoint در ابتدای اجرا لازم است. صرف PDF، اجرای تاریخی را اثبات نمی‌کند.

### ترتیب اولویت

| اولویت | کار | اثر بر اعتبار مقاله |
|---|---|---|
| P0 | موجودی شواهد و runner قابل بازتولید | تعیین می‌کند چه چیزی واقعاً قابل اجراست |
| P1 | ممیزی اجرایی PGD/TEMP و انتخاب candidate | مانع مقایسه بر اساس خروجی ضعیف‌تر از candidateهای واقعاً یافته‌شده می‌شود |
| P2 | تنظیم حملات روی validation و تثبیت پروتکل | بهبود قدرت حمله بدون تنظیم مکرر روی test |
| P3 | official-test QSNN و SNN، سپس چند frontend مستقل | اصلی‌ترین خلأ تجربی نسخهٔ فعلی را پوشش می‌دهد |
| P4 | classical-head و circuit ablation | تفسیر نقش head را از حدس به مقایسهٔ کنترل‌شده نزدیک می‌کند |
| P5 | نمونهٔ واقعی، تحلیل state–margin و نمودارهای نهایی | ایده را به شواهد قابل مشاهده وصل می‌کند |
| مؤخر | بازسازی مطالعهٔ grid و دفاع/monitor | پس از تثبیت مطالعهٔ اصلی؛ جدا از هستهٔ حداقلی این مرحله |

**در این مرحله هیچ هدفی برای افزایش ASR یا اثبات برتری TEMP تعیین نکن.** اگر حملات نزدیک‌اند یا head کوانتومی مزیتی ندارد، همان نتیجه با شواهد کافی گزارش شود.

## 1. حفظ شواهد و تفکیک اجراها

1. دستورهای مخزن، وضعیت Git و تغییرهای کاربر را بررسی کن. `guide.md` حذف‌شده را بازسازی نکن؛ phase2.md و داده‌های تاریخی را بازنویسی نکن.
2. commit فعلی کد و شناسهٔ snapshot تاریخی را جدا ثبت کن. snapshot تاریخی `80d02f5733d4…` منشأ گزارش‌های قبلی است؛ اجراهای جدید باید commit/config خود را داشته باشند.
3. کد PGD تاریخی را برای اصلاح silent تغییر نده. نسخهٔ جدید با شناسهٔ مستقل و گزارش مقایسه بساز؛ اعداد پیشین با نتایج تازه جایگزین بی‌توضیح نشوند.
4. برای هر نتیجه یکی از وضعیت‌های `historical_report_only`، `recovered_artifact`، `replayed` یا `new_experiment` ثبت شود.
5. مقدار ناشناخته `null`/`unknown` باشد، نه صفر. experiment ناتمام یا unavailable در ASR وارد نشود.
6. test set فقط برای ارزیابی نهایی استفاده شود؛ تنظیم معماری، attack hyperparameter و انتخاب نتیجهٔ مطلوب روی test انجام نشود.

### ساختار خروجی پیشنهادی

مسیرها را با ساختار واقعی پروژه تطبیق بده و اگر فایل معادل وجود دارد از همان استفاده کن:

```text
Reports/phase3/
  inventory.json
  preregistration.yaml
  pilot.json
  execution_status.json
  selection_audit.json
  verification.json
  report.md
configs/phase3/
scripts/phase3/
results/phase3/<run_id>/
  config.yaml
  environment.json
  manifest.csv
  per_example.parquet       # یا JSONL با schema مستند
  timings.jsonl
  aggregates.json
  trajectories/            # subset مستند برای trace کامل
  exemplars/
figures/phase3/
```

فایل بزرگ checkpoint یا raw dataset را صرفاً برای گزارش‌نویسی به Git اضافه نکن؛ محل، hash و دستور دسترسی/بازتولید ثبت شود.

## 2. P0 — موجودی شواهد و آزمون قابلیت اجرا

### 2.1 بررسی فایل‌های واقعاً موجود

فهرست checkpointهای frontend و QSNN، dataset، split IDs، attack manifests، config، raw logits/probabilities، trajectoryها، timing arrays و source معماری‌ها را بساز. از مسیرهای معرفی‌شده در phase2 و supplement شروع کن؛ بازسازی مسیر از روی حدس کافی نیست.

برای هر artifact این موارد لازم‌اند:

```text
artifact_id, role, path, exists, size_bytes, sha256,
source_commit, training_seed, split_id, model_id,
compatible_with_current_loader, evidence_status, missing_fields
```

وجود یک فایل با پسوند `.pt` به معنی وجود victim صحیح نیست. معماری، state_dict keys، preprocess، hash و seed آن باید سازگار باشند. وزن‌های مفقود را با seed تنها بازسازی‌شده فرض نکن.

### 2.2 محیط اجرا و pilot

- نسخهٔ Python/PyTorch/CUDA، GPU/CPU، RAM/VRAM، dtype، batch/chunk size و تنظیم determinism ثبت شوند.
- یک smoke run کوچک با checkpoint واقعی و دادهٔ موجود اجرا کن: clean prediction، forward/backward timestamp، یک candidate معتبر و hard-forward verification.
- زمان و peak memory واقعی اندازه‌گیری شود؛ ETA campaign از pilot به دست آید، نه حدس ثابت ساعت/روز.
- ابتدا correctness، سپس تنظیم chunk برای حافظه. تغییر chunk، dtype یا caching همراه run config ثبت شود.
- محدودیت منابع موجود پروژه رعایت و اجراها checkpoint/resume داشته باشند. اگر زیرساخت مناسب نیست، runnable code و config را تکمیل و بخش اجرای وابسته را `blocked_resource` گزارش کن؛ کاهش silent تعداد نمونه یا مدل انجام نشود.

### 2.3 مسیر جایگزین برای شواهد مفقود

| وضعیت | اقدام |
|---|---|
| checkpoint و دادهٔ اصلی موجود | replay روی manifest اصلی و مقایسه با گزارش |
| checkpoint موجود، manifest تاریخی غایب | آزمایش تازه با manifest جدید؛ نام replay نگذار |
| checkpoint غایب، train code و داده موجود | pipeline تازه با config ثابت آموزش بده؛ نتیجهٔ جدید، نه بازتولید دقیق وزن تاریخی |
| کد مدل یا دادهٔ ضروری غایب | مسیر وابسته blocked؛ inventory و runnerهای قابل تکمیل ادامه یابند |
| grid artifacts غایب، QSNN قابل اجرا | مطالعهٔ اصلی QSNN را ادامه بده؛ grid مانع همهٔ Phase 3 نشود |

**خروجی پایان P0:** inventory، فهرست اختلاف‌ها، نتیجهٔ smoke run و pilot اندازه‌گیری‌شده. قبل از درست‌بودن clean pipeline، campaign کامل اجرا نشود.

## 3. P1 — ممیزی اجرایی حمله و selection

### 3.1 مقایسهٔ دو قانون انتخاب روی دقیقاً همان candidateها

برای هر اجرای PGD، candidate تمیز و تمام iterateها را با hard forward واقعی ارزیابی کن و سه مورد را نگه دار:

1. `legacy_output`: candidate منتخب قانون تاریخی maximum CE.
2. `any_valid_success`: آیا حداقل یک candidate **معتبر** misclassified شده است؟
3. `success_priority_output`: در صورت وجود موفقیت معتبر، یک candidate موفق با tie-break ثابت؛ در غیر این صورت بهترین loss.

برای این audit، مسیر جست‌وجو، seed و تعداد candidateها یکسان باشند؛ فقط قانون reporting/selection فرق کند. تغییر جست‌وجو را در آزمایش جدا ارزیابی کن.

برای TEMP نیز موفقیت واقعی همهٔ candidateها بر اساس argmax ثبت شود. margin صفر می‌تواند tie باشد؛ موفقیت را صرفاً `margin < 0` یا `margin <= 0` فرض نکن. قانون tie در classifier مستند باشد.

قواعد موفقیت:

```text
valid = event_identity_ok AND coordinates_ok AND polarity_ok
        AND count_ok AND timestamp_bounds_ok AND ordered_ok
success = valid AND (hard_forward_argmax != true_label)
any_valid_success = OR(success over evaluated candidates)
```

برای تمام حملات، مخرج و شرط clean correctness یکسان و از قبل ثابت باشد. verification forwardهای audit را از forwardهای داخل search جدا بشمار. audit را با زمان تاریخی search مخلوط نکن.

**گزارش لازم:** تعداد مثال‌هایی که `legacy_output` شکست می‌خورد ولی `any_valid_success` موفق است، شناسهٔ مثال، اولین گام موفق و اختلاف نهایی ASR. اگر اختلاف صفر است، همان صفر گزارش شود. بدون trajectory یا اجرای واقعی، وجود چنین اختلافی ادعا نشود.

### 3.2 بررسی مدل و preprocessing

- clean forward تکراری برای یک نمونه، پس از callهای دیگر و با ترتیب متفاوت، همان نتیجهٔ مورد انتظار را بدهد.
- reset membrane/accumulator و eval mode در مسیر واقعی runner بررسی شوند؛ ممیزی timestamp به grid تعمیم داده نشود.
- شکل و دامنهٔ tensor، bin edges ثابتِ حاصل از clean endpoints، cap=255 و frontend scaling صحیح باشند.
- تغییر input ترتیب/بچ candidateها نباید اختلاف عددی غیرمنتظره یا state leakage ایجاد کند؛ tolerance با dtype و اندازهٔ margin توجیه شود.
- identity، spatial coordinates، polarity و تعداد رویدادها مستقیماً با raw input مقایسه شوند؛ checksum صرفاً روی tensor aggregated کافی نیست.
- operator feasibility باید bounds و monotonicity را روی خروجی نهایی پاس کند. count preservation را با stealth یکی ندان.

### 3.3 گرادیانِ surrogate در برابر hard forward

این pipeline دارای hard binning و surrogate backward است. مشتق finite-difference بسیار کوچک در ناحیهٔ ثابت binها می‌تواند صفر باشد؛ عدم تطابق آن با surrogate به‌تنهایی bug نیست.

دو بررسی جدا لازم‌اند:

1. صحت autograd روی اجزای واقعاً differentiable با dtype/tolerance مناسب و ورودی‌های دور از نقاط nondifferentiable.
2. usefulness جهت surrogate با perturbationهای feasible و اندازه‌های متناسب با bin boundary، همراه loss/prediction واقعی. surrogateهای جایگزین روی validation مقایسه شوند؛ گرادیان صفر یا اشباع بعد از clipping/capping گزارش شود.

تست‌های هدفمند برای validity، state reset و selection نوشته شوند؛ تستی که فقط کد خودش را تکرار می‌کند ارزشی ندارد. یک toy multiclass case می‌تواند نشان دهد maximum CE لزوماً candidate موفق را انتخاب نمی‌کند؛ این test اثر آن بر نتایج تاریخی را اثبات نمی‌کند.

### 3.4 تفاوت radius و query budget

در گزارش قبلی TEMP با بودجهٔ دسترسی در ۵٪ چهار موفقیت و در ۱۰٪ سه موفقیت دارد. feasible set بزرگ‌تر است، اما جست‌وجوی محدود می‌تواند نتیجهٔ ضعیف‌تری پیدا کند؛ این افت خودبه‌خود bug نیست.

- `standalone ASR` هر radius جدا گزارش شود.
- در runner تازه می‌توان best valid candidate شعاع کوچک‌تر را پس از اعتبارسنجی، در شعاع بزرگ‌تر نیز نگه داشت و `cumulative ASR` جدا ارائه کرد.
- candidateهای منتقل‌شده و هزینهٔ جست‌وجوی تولیدشان ثبت شوند؛ cumulative result با query budget مستقلِ یک radius برابر معرفی نشود.
- best-so-far ASR در یک trajectory با افزایش تعداد candidateهای همان اجرا نباید کاهش یابد. این property با آزمون بررسی شود.

## 4. P2 — افزایش قدرت حمله بدون انفجار تعداد اجراها

### 4.1 pilot روی validation، سپس تثبیت config

به‌جای full factorial بزرگ، مرحله‌ای عمل کن:

1. روی همان manifest تاریخی، اگر موجود است، baseline literal را replay کن. شناسهٔ نمونه‌ها برای مقایسهٔ زوجی یکسان باشد.
2. یک development subset ثابت و stratified از validation برای tuning حمله تعیین کن و manifest آن را ثبت کن. آن را test ننام.
3. برای PGD از baseline شروع کن؛ سپس iterationهای پیشنهادی 20، 50 و 100 و step sizeهای نسبی محدود را بررسی کن. الگوی اولیهٔ step size: `epsilon/5`، `epsilon/10` و `epsilon/20`. این‌ها انتخاب‌های آغازین‌اند، نه تنظیمات اثبات‌شدهٔ بهینه.
4. lossهای CE و untargeted logit margin و restartهای پیشنهادی 1 و 5 را مرحله‌ای بررسی کن. `1` در legacy به معنی clean start بدون random restart است؛ تفاوت با یک random start دقیق ثبت شود.
5. فقط ترکیب‌های مفید از مرحلهٔ قبلی به campaign بزرگ منتقل شوند. نتیجهٔ negative نیز حفظ شود؛ انتخاب بر پایهٔ validation و هزینهٔ ثبت‌شده باشد.
6. برای TEMP، scheduleهای literal Q=21 و Q=41 و budgetهای بزرگ موجود بازتولید شوند. curve جدید فقط بر اساس واقعی‌ترین total proposal count و چند attack seed ثبت‌شده ساخته شود.
7. حداقل یک مقایسهٔ loss-matched با margin برای PGD و TEMP انجام شود تا تفاوت objective با تفاوت optimizer اشتباه نشود.

عددهای بالا طرح پیشنهادی‌اند. هر تغییر ناشی از منابع قبل از test در config ثبت شود؛ از نتیجهٔ test برای انتخاب تنظیم «بهتر» استفاده نکن.

### 4.2 بودجهٔ منصفانه و هزینهٔ واقعی

سه تعریف candidate، forward و elapsed time همچنان جدا بمانند. برای هر condition ثبت شود:

```text
requested_Q, actual_Q, unique_candidates, evaluated_candidates,
search_forward_calls, backward_calls, verification_forward_calls,
candidate_chunk, examples_per_batch, elapsed_search_seconds,
elapsed_verification_seconds, device, precision, peak_memory
```

Forward call و تعداد candidate یکی نیستند؛ TEMP می‌تواند تعداد زیادی candidate را در یک call بچ کند. در صورت استفاده از «forward count»، واحد مقصود، candidate-equivalent و batch size را روشن تعریف کن؛ تعداد API call به‌تنهایی معیار کار محاسباتی نیست.

بر اساس گزارش phase2، TEMP با chunk تا 64 و PGD با یک مثال اجرا شده‌اند. این می‌تواند مقایسهٔ کارایی implementation واقعی باشد، اما برابری هزینهٔ oracle یا برابری الگوریتمی را اثبات نمی‌کند.

- پروتکل batched فعلی حفظ و دقیق گزارش شود.
- sensitivity کم‌هزینه با candidate evaluation سریالی TEMP یا chunkهای ثابت کوچک‌تر روی pilot انجام شود؛ نتیجه به کل campaign تعمیم داده نشود.
- warm-up، synchronization، CUDA state، GPU و dtype در هر اجرای تازه ثبت شوند.
- calibration از train/development جدا از test IDs استفاده کند؛ median، IQR و تعداد تکرارهای واقعی ذخیره شوند. بودجهٔ time را برای هر config/model/device تازه با همان rule ثابت کالیبره کن.
- budget-matched به معنی equality دقیق زمان نباشد؛ ratio و dispersion اندازه‌گیری‌شده گزارش شود.
- forward reuse یا caching در runner تازه هزینه را تغییر می‌دهد؛ نتیجهٔ historical literal و optimized implementation تفکیک شوند.

## 5. P3 — ارزیابی official test و تکرار مدل‌ها

### 5.1 تثبیت پیش از test

در `preregistration.yaml` پیش از اجرای نهایی ثبت کن: dataset version، splitها، مدل، preprocessing، checkpoint-selection rule، attack configها، radiusها، seeds، نمونه‌گیری، بودجهٔ زمان/دسترسی و معیارهای اصلی. این فایل می‌تواند ثبت داخلی پروتکل باشد؛ ثبت عمومی یا external submission لازم نیست.

موارد زیر روی validation انتخاب شوند: architecture، checkpoint، hyperparameter آموزش و hyperparameter حمله. تغییر بعدی ثبت و به‌عنوان تحلیل exploratory از نتیجهٔ اصلی جدا شود.

### 5.2 clean test و attack populations

1. clean accuracy همهٔ QSNN/SNNهای نهایی روی **تمام ۱۰هزار نمونهٔ official test** اندازه‌گیری شود؛ تعداد correct، macro-F1 و class counts ذخیره شوند.
2. برای مقایسهٔ زوجی مدل‌ها، هدف اولیه `n=1000` نمونهٔ مشترک clean-correct است؛ انتخاب با sampling seed ثابت و stratification طبق rule از پیش ثبت‌شده باشد، نه first-1000 بدون بررسی ترتیب dataset.
3. اگر class سهمیهٔ کافی ندارد، n واقعی و rule تخصیص باقی‌مانده ثبت شود؛ تکرار مصنوعی نمونه یا ساخت نتیجه مجاز نیست.
4. برای مقایسهٔ حملات روی یک مدل، manifest مشترک بین حملات و budgetها باشد.
5. manifest joint-correct estimand را محدود می‌کند؛ در کنار آن clean accuracy کامل و، اگر منابع اجازه دهد، ارزیابی روی نمونه‌های clean-correct خود هر مدل با مخرج مستقل گزارش شود. این دو نرخ با هم pool نشوند.
6. اگر benchmark کامل روی همهٔ testها انجام نشده، `clean_accuracy × (1−ASR_subset)` را robust test accuracy ننام. نام مناسب `survival under evaluated attacks on selected clean-correct subset` است.

مرحلهٔ اولیهٔ اجرای صحیح می‌تواند روی یک victim موجود باشد؛ آن را نتیجهٔ چندseed ننام. بعد به pipelineهای مستقل گسترش بده.

### 5.3 استقلال seed

هدف عملی پیشنهادی: دست‌کم سه pipeline با frontendهای مستقل، مثلاً seedهای 42، 123 و 777؛ در صورت منابع کافی پنج pipeline. سه seed تضمین قدرت آماری یا حداقل عمومی پذیرش نیست.

برای هر seed، آموزش frontend و ادامهٔ head مستقل و منشأ pretraining ثبت شود. سه head متفاوت روی frontend مشترک، سه pipeline مستقل محسوب نمی‌شود. اگر frontend مشترک عمداً کنترل ablation است، همان طرح conditional نامیده شود.

مدل‌ها بر اساس validation انتخاب شوند، نه بیشترین accuracy یا ASR test. sampling examples و attack stochastic seeds مستقل از training seeds و در config مشخص باشند.

### 5.4 آمار

- numerator/denominator هر cell، ASR و Wilson interval همراه محدودیت مدل دوجمله‌ای گزارش شود؛ selected/stratified subset به‌تنهایی نمونه‌گیری تصادفی از کل جمعیت نیست.
- مقایسهٔ حملات روی نمونه‌های مشترک: counts `both/PGD-only/TEMP-only/neither`، اختلاف زوجی و exact McNemar با convention صفر discordance.
- interval اختلاف دو ASR مستقل را با اختلاف زوجی جایگزین نکن. در صورت paired bootstrap، example ID واحد resampling و دو خروجی همان مثال با هم جابه‌جا شوند.
- تکرارهای attack seed یا model seed روی همان examples، نمونه‌های آماری مستقل اضافی نیستند. نتایج هر seed جدا و summary بین مدل‌ها ارائه شوند؛ pooling سادهٔ `3 × 1000` به‌عنوان ۳۰۰۰ موضوع مستقل انجام نشود.
- در صورت ادعای آزمون تأییدی، مقایسه‌های اصلی و خانوادهٔ multiplicity پیشاپیش مشخص و rule تعدیل مانند Holm ثبت شود؛ بقیه exploratory باشند. ادعای equivalence از p-value بزرگ ساخته نشود.
- هدف گزارش تفاوت و عدم‌قطعیت است؛ افزایش n فقط برای رسیدن به p<0.05 انجام نشود.

## 6. P4 — ablation با بیشترین ارزش علمی

### 6.1 مرحلهٔ کنترل‌شده با frontend ثابت

از یک frontend ثابت و split یکسان شروع کن و headها را تحت بودجهٔ training و انتخاب checkpoint یکسان مقایسه کن:

| Variant | نقش |
|---|---|
| Q-head کامل | مدار و readout فعلی |
| Classical head | nonlinear head کلاسیک روی همان latent، با ظرفیت نزدیک و پارامتر/زمان دقیق گزارش‌شده |
| Q-head بدون entangling gates | حذف CNOTها، حفظ encoding، rotations و readout؛ آموزش مجدد |

انتخاب architecture کلاسیک بر پایهٔ validation و پیش از test باشد. نزدیک‌بودن parameter count به معنی برابر بودن expressivity یا training difficulty نیست؛ هر دو هزینه و عملکرد اندازه‌گیری شوند.

حذف gate از مدل آموزش‌دیده بدون retraining یک intervention پس از آموزش است؛ آن را ablation آموزش‌دیده معرفی نکن. اگر این intervention هم بررسی شد، جدا گزارش شود.

در Q-head بدون entanglement، readout تمام 256 احتمالِ حاصل از حالت ضربی همچنان feature map غیرخطی ایجاد می‌کند؛ آن را «مدل خطی کلاسیک» ننام.

ابتدا frontend برای همه frozen باشد تا نقش head واضح‌تر شود. در صورت اجرای مرحلهٔ fine-tune، schedule و frontend initialization برای همه variantها یکسان و نتایج از حالت frozen جدا باشند.

### 6.2 چه چیزی باید گزارش شود؟

- clean validation/test، conditional attack success، margins، total/head parameter count و training/search cost.
- یک protocol حملهٔ مشترک و حداقل sanity check قدرت optimizer برای همه variantها؛ ضعف گرادیان یک variant نباید به‌عنوان برتری robust آن تعبیر شود.
- failureهای مشترک و اختصاصی روی joint manifest؛ تفاوت مخرج‌ها صریح.
- نتیجهٔ منفی مجاز است؛ نبود برتری quantum head را پنهان نکن.

این ablation فقط برای همین داده و طرح کنترل‌شده شواهد می‌دهد؛ به‌تنهایی quantum advantage یا علت یکتای failure را اثبات نمی‌کند.

## 7. P5 — دادهٔ هر نمونه، توضیح مکانیزم و شکل واقعی

### 7.1 حداقل schema برای رکورد هر نمونه

```text
run_id, source_commit, dataset_split, example_id, true_label,
model_id, training_seed, attack_seed, attack_name, selection_rule,
budget_type, budget_value, clean_pred, attacked_pred,
clean_logits, attacked_logits, clean_margin, attacked_margin,
validity_pass, success, first_success_candidate,
event_count, realized_linf_time, realized_l1_time,
num_shifted_events, hard_bin_changes,
candidate_count, forward_count, backward_count,
search_seconds, verification_seconds,
clean_state_ref, attacked_state_ref, evidence_status
```

raw timestamps، probability vectors و statevectors را با ID/hash و فایل همراه متصل کن؛ نیاز نیست همهٔ آرایه‌ها در CSV فشرده شوند. برای همهٔ candidateها حداقل loss، prediction، validity و هزینه نگه دار؛ trajectory کامل raw events می‌تواند برای subset از پیش مشخص و همهٔ مثال‌های اختلاف selection ذخیره شود.

### 7.2 تحلیل state–margin در مدل نهایی

مدل فعلی analytic و حالت خالص هشت‌کیوبیتی دارد. در صورت دسترسی به statevector نرمال‌شده، بدون ساخت density matrix بزرگ می‌توان محاسبه کرد:

\[
F=|\langle\psi|\psi'\rangle|^2,
\qquad D_{\mathrm{tr}}=\sqrt{1-F},
\qquad TV(q,q')=\tfrac12\|q-q'\|_1.
\]

این تعریف F، squared fidelity برای حالت‌های خالص است. normalization، tolerance و clamp خطای کوچک floating point به [0,1] ثبت شود؛ خطای عددی بزرگ با clamp پنهان نشود. در صورت noise/حالت mixed این فرمول حالت خالص به کار نرود.

بررسی‌های اصلی:

1. `TV <= D_tr` تا tolerance عددی.
2. برای هر رقیب، margin واقعی با lower bound مقاله سازگار باشد.
3. موفقیت/بقا بر حسب clean margin، realized distortion، state distance و تغییر probabilities بررسی شود؛ فقط مقایسهٔ میانگین fidelity کافی نیست.
4. در صورت مدلسازی آماری، تعداد failureهای اندک فعلی برای مدل چندمتغیرهٔ پیچیده کافی فرض نشود؛ تحلیل توصیفی و نمودارهای هر نمونه اولویت دارند.
5. state distance زیر measurement-basis unitary مشترک تغییر نمی‌کند، ولی measurement probabilities و حساسیت readout مرتبط‌اند؛ نقطهٔ برداشت state در کد مشخص باشد.

فاصلهٔ state برای **تمام** نمونه‌های تحلیل‌شده ذخیره شود، نه صرفاً موفقیت‌های چشمگیر. ارتباط مشاهده‌شده علت کوانتومی failure را به‌تنهایی اثبات نمی‌کند.

### 7.3 انتخاب نمونهٔ واقعی و شکل‌ها

پس از داشتن raw data، یک rule ثابت برای exemplar انتخاب کن؛ مثلاً اولین مثال معتبر در هر گروه outcome طبق manifest. از انتخاب فقط موارد نمایشی و تعمیم آن‌ها خودداری کن.

شکل exemplar می‌تواند این پنل‌ها را داشته باشد:

- raster زمانی clean/retimed روی خطوط مشخص، با واحد زمان و حفظ ID؛
- histogram جابه‌جایی و تغییر bin counts واقعی؛
- clean/attacked logits یا true-class margin؛
- در صورت موجودبودن، probabilities/state-distance همان نمونه.

اگر همهٔ رویدادها نمایش داده نمی‌شوند، sampling بصری و تعداد نقاط نشان‌داده‌شده صریح باشد؛ حساب validity روی کل رویدادها انجام شود.

شکل‌های نتیجهٔ جدید:

1. **ASR در برابر هزینهٔ واقعی:** candidate، forward-equivalent و زمان در پنل‌های جدا، با best-so-far و تعریف دقیق cumulative cost.
2. **paired difference/overlap:** نتایج هر مدل و seed، بدون pool مستقل‌نمایانه.
3. **ablation یا state–margin:** فقط پس از اجرای واقعی؛ جایگزینی بعضی شکل‌های تکراری با شواهد جدید.

## 8. اصلاح‌های کوچک باقی‌مانده در PDF فعلی

این موارد مانع اجرای آزمایش‌ها نیستند و در پایان همراه نتایج تازه انجام شوند:

- **شکل ۱، صفحهٔ ۳:** مسیر و مدار بهتر شده‌اند، اما فونت gateها در اندازهٔ چاپ کوچک است. اندازهٔ نهایی را بررسی کن؛ در صورت نیاز مدار تفصیلی به supplement و overview خواناتر به main برود. به‌جای ریزکردن بیشتر فونت، layout ساده شود.
- **شکل ۲، صفحهٔ ۶:** برچسب `Access` برای دو resource متفاوت استفاده شده است. برچسب `Candidate / forward (same aggregate counts)` یا کلید صریح مناسب‌تر است. یکسانی aggregate counts یا حتی جدول overlap در هر شرط، هویت یکسان شکست‌ها بین دو شرط را اثبات نمی‌کند؛ برای ادعای نمونه‌های یکسان، IDs لازم‌اند.
- **شکل ۲، پنل overlap:** گروه Neither با ۹۵ تا ۹۷ مثال، تفاوت‌های ۱ تا ۲ مثالی را می‌پوشاند. نمای اصلی ۱۰۰مثالی حفظ و zoom/پنل کمکی فقط برای attacked union با مخرج واضح اضافه شود، یا جدول کوچک زوجی جایگزین شود. محور را بی‌توضیح قطع نکن.
- **شکل ۳، صفحهٔ ۷:** برخی برچسب‌های مقادیر کوچک در inset نزدیک‌اند؛ هم‌پوشانی در اندازهٔ چاپ و رنگ خاکستری بررسی شود. این شکل صرفاً کنترل جدا باقی بماند تا منشأ baselineها قابل تأیید شود.
- تعداد منابع اکنون ۲۰ است. برای افزایش شمارش دوباره برنامه نچین؛ فقط منبع روش تازه یا خلأ مشخص، مانند interval آماری، اضافه شود و metadata تأیید شود.
- اگر venue داوری دوطرفهٔ ناشناس دارد، لینک repository و اطلاعات هویتی مطابق سیاست همان venue بررسی شوند؛ بدون دانستن venue الزام عمومی برای حذف لینک فرض نکن.

## 9. مطالعهٔ grid و monitor: دامنهٔ جدا

### Grid

در صورت بازیابی کد و checkpointها، reset/preprocessing، نسخهٔ معماری، feasibility/capacity، penalty و اثر انتخاب candidate ممیزی اجرایی شوند. ضریب تاریخی B0 فقط با سند تعیین شود.

اگر ضریب تاریخی حل نشد ولی مطالعهٔ تازه ممکن است، sensitivity پنج و ده با config روشن اجرا و به‌عنوان **آزمایش جدید** گزارش شود؛ از این طریق مقدار تاریخی استنتاج نشود. اگر artifacts پیدا نشدند، grid در نقش contextual/historical باقی بماند و سهم اصلی ادعای causal آن نباشد.

### Monitor / tomography / defense

این مسیر را فعلاً وارد هستهٔ Phase 3 نکن. قبل از ROC/PR باید observable، shot budget، clean calibration، threshold و policy پاسخ تعریف شوند؛ پس از آن adaptive attack لازم است. افزودن بخش دفاع بدون اجرای آن داستان مقاله را دوباره پراکنده می‌کند.

## 10. حداقل بستهٔ علمی مطلوب و معیار پایان

هدف عملی برای پایان هستهٔ Phase 3:

- [ ] موجودی و provenance قابل بررسی؛ اجرای تازه با artifact واقعی، نه فقط گزارش.
- [ ] ممیزی selection روی candidateهای یکسان و شمارش any-valid-success برای هر دو حمله.
- [ ] تنظیم حمله روی development و config نهایی ثابت پیش از test.
- [ ] clean test کامل QSNN/SNN و attack test با manifest و مخرج روشن؛ هدف اولیه ۱۰۰۰ مثال مشترک.
- [ ] نتیجهٔ هر seed مستقل؛ هدف پیشنهادی حداقل سه frontend مستقل در صورت امکان منابع.
- [ ] budget curve و حداقل یک مقایسهٔ loss-matched.
- [ ] classical-head ablation؛ برای تعبیر entanglement، variant بدون entangler با retraining.
- [ ] حداقل یک exemplar واقعی و خروجی‌های هر نمونه با rule انتخاب مستند.
- [ ] گزارش جداگانهٔ missing/blocked و حساسیت نتایج به محدودیت‌ها.

هیچ شرطی برای «برتری آماری TEMP»، «دقت بالاتر QSNN» یا «ASR دلخواه» معیار پایان نیست. این بسته تضمین پذیرش نیست؛ هدف، تبدیل نتیجهٔ گزارش‌محور به مطالعهٔ اجرایی و قابل ارزیابی است.

اگر فقط بخشی ممکن شد، phase3 کامل اعلام نشود. برای هر مورد یکی از وضعیت‌های `not_started`، `implemented`، `smoke_passed`، `running`، `completed`، `failed` یا `blocked` همراه دلیل و artifact ثبت شود. وجود script برابر completed experiment نیست.

## 11. بررسی نهایی، مقاله و تحویل

1. unit/integration checks هدفمند validity، selection، reset، budget و aggregation اجرا شوند.
2. aggregates مستقیماً از per-example records ساخته شوند؛ شکل و جدول از یک منبع ماشینی بخوانند.
3. experimentهای ناتمام، invalid candidate و clean-incorrect با rule مستند مدیریت شوند. invalid candidate موفقیت نیست؛ اگر کل اجرای یک مثال خراب شد آن را survivor فرض نکن. مخرج از پیش انتخاب‌شده را با حذف silent مثال‌های سخت تغییر نده: run کامل نامعتبر باید تکرار یا همراه تعداد missing جدا گزارش شود، و برای search معتبر همیشه candidate تمیزِ معتبر به‌عنوان fallback وجود داشته باشد.
4. runtime، داده و seed در هر گزارش resolve شوند؛ provenance قدیمی و تازه با هم مخلوط نشوند.
5. نتایج تازه با uncertainty و claim متناسب وارد Results شوند؛ اگر نتیجه با تاریخی فرق دارد، تفاوت protocol/selection یا عدم بازتولید توضیح داده شود.
6. Abstract و Conclusion بر اساس نتیجهٔ واقعی نهایی بازنویسی شوند؛ محدودیت حل‌نشده حذف نشود.
7. main و supplement با backend پروژه کامپایل، logs و PDF صفحات شکل‌ها بصری بررسی شوند. build موفق به‌عنوان تأیید نتایج تجربی معرفی نشود.
8. گزارش نهایی شامل فایل‌های تغییرکرده، configهای اجرا، تعداد completed/blocked، نتیجهٔ selection audit، clean/attack test، seedها، runtime و اقدامات باقی‌مانده باشد.

هیچ commit، push یا بارگذاری Overleaf در این فایل درخواست نشده است. تغییر نامرتبط کاربر و داده‌های تاریخی حفظ شوند.

## 12. دستور کوتاه شروع برای Codex

> phase3.md را کامل بخوان. Phase 2 را تکرار نکن. ابتدا P0 را با موجودی واقعی artifacts و smoke/pilot اجرا کن، سپس P1 را روی candidateهای یکسان پیاده و اجرایی بررسی کن. هر مورد ممکن را با حفظ داده‌های تاریخی ادامه بده؛ اگر artifact خاصی غایب است، فقط مسیر وابسته را blocked علامت بزن و از مسیر جایگزین مستند استفاده کن. تنظیم حمله روی development انجام و پیش از official test ثابت شود. خروجی‌های هر نمونه، config، هزینه و provenance را ذخیره کن. سپس P2 تا P5 را به‌ترتیب وابستگی و منابع اجرا کن؛ script آماده را با آزمایش انجام‌شده یکی ندان. هیچ نتیجه‌ای برای پرکردن جدول نساز و موفقیت را به نفع یک مدل هدف‌گذاری نکن. مقاله و شکل‌ها فقط از نتایج تأییدشده به‌روز شوند. در پایان گزارش واقعی completed/blocked و وضعیت build بده.
