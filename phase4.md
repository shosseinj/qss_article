# Phase 4 — داوری علمی، رفع ناسازگاری مخزن و مقاله، تکمیل منابع و شواهد

**مقاله:** Temporal Retiming Attacks on Hybrid Quantum Spiking Classifiers  
**نسخهٔ مبنا:** `main(3).pdf`، ۸ صفحه  
**مخزن بررسی‌شده:** https://github.com/shosseinj/ABC_def1  
**HEAD دریافت‌شده هنگام این بررسی:** `80d02f5733d4cbe7c3e69b828dff66d50ba5c211`  
**تاریخ بررسی:** ۱۴ اکتبر ۲۰۲۶  
**نوع خروجی:** داوری داخلیِ نویسنده و دستور اصلاح برای Codex؛ این فایل به معنی اجرای Phase 4 یا تصمیم یک مجله نیست.

## 1. نتیجهٔ داوری و حدود بررسی

مقاله از نظر صداقت در حدود ادعا، تفکیک دو threat model و نمایش نتایج بهتر شده است. شمارش‌های موجود، p-valueهای زوجی و بازه‌های Wilson شکل ۲ با یکدیگر سازگارند. با این حال، هنوز شاهد اصلی روی ۱۰۰ نمونهٔ انتخاب‌شدهٔ validation و یک victim seed است؛ official-test QSNN، ممیزی اجرایی selection و ablation مدل نهایی در مقاله ارائه نشده‌اند. سهم تجربی هنوز برای نتیجه‌گیری گسترده دربارهٔ QSNN یا برتری یک حمله محدود است.

این داوری شامل مطالعهٔ PDF، مقایسه با نسخهٔ قبلی، مشاهدهٔ شکل‌ها، دریافت درخت Git و خواندن فایل‌های مشخص کد و گزارش بوده است. آموزش، حمله، loading وزن‌ها یا بازتولید مستقل مدل‌ها در این بررسی انجام نشده‌اند. فایل supplement جدید و تغییرهای pushنشدهٔ کامپیوتر کاربر در دسترس این بررسی نبوده‌اند.

**یافتهٔ مهم مخزن:** کد baselineهای grid در مخزن عمومی وجود دارد. ادعای قبلی «نبود تعریف baselineها» فقط دربارهٔ بستهٔ محدود شواهد صدق می‌کرد؛ نباید به کل مخزن تعمیم داده شود. در مقابل، configs، checkpointها و پیوند قطعی همهٔ کدها به اجرای تاریخی همچنان نیازمند بررسی‌اند.

فاز چهارم باید دو مسیر را هم‌زمان پیش ببرد:

- اصلاح‌های قابل انجام اکنون: ناسازگاری متن و کد، تعریف بودجه، بیان contribution، منابع، caption و صفحه‌آرایی.
- تکمیل شواهد اجرایی: باقی‌ماندهٔ Phase 3، با استفادهٔ مجدد از نتایج واقعاً کامل‌شده و بدون بازاجرای بی‌دلیل.

اگر فقط مسیر اول انجام شد، فاز چهارم از نظر تجربی کامل نیست.

## 2. شواهد تازه از مخزن: اصلاح برداشت‌های قبلی

لینک هر فایل زیر را می‌توان با این پیشوند و مسیر نسبی باز کرد:

`https://github.com/shosseinj/ABC_def1/blob/80d02f5733d4cbe7c3e69b828dff66d50ba5c211/`

| مشاهدهٔ مستقیم | شاهد | نتیجهٔ مجاز |
|---|---|---|
| loader چهار مدل موجود است | `experiments/nmnist/controlled_models.py`، خطوط 7–29 | تعریف baselineها قابل مطالعه است؛ نبود checkpoint هنوز موضوع جداست |
| `convnet` به `SimpleNet_v2` وصل است | همان فایل، خط 28؛ `reference_models/simplenet.py` | این baseline دارای LIF است؛ ConvNet را خودکار ANN/ReLU فرض نکن |
| reset در forward مدل‌های مرجع دیده می‌شود | `reference_models/resnet.py`، `simplenet.py` و `vgg.py` | شواهد ایستا برای reset وجود دارد؛ رفتار واقعی checkpoint/batching هنوز باید آزمایش شود |
| کد آموزش و حملهٔ grid موجود است | `scripts/train_nmnist_controlled_four_models.py` و `scripts/run_nmnist_controlled_attack.py` | عبارت «کد اجرا غایب است» برای کل مخزن دقیق نیست |
| gate آموزش به test accuracy وابسته است | فایل آموزش، خطوط 74–79 و 143–156 | خطر استفاده از test برای تصمیم توسعه وجود دارد؛ وقوع واقعی بدون history/log اثبات نشده است |
| adapter مربوط به B0 موجود است | `experiments/nmnist/official_pil_adapter_batched.py`، خطوط 249–262 | باید default سازندهٔ upstream هم بررسی شود؛ عدد پنج هنوز از این خطوط به‌تنهایی تأیید نمی‌شود |
| ablation قدیمی QSNN موجود است | `results/nmnist_qsnn_ablation_report.md` و اسکریپت متناظر | مطالعهٔ توسعهٔ مدل قدیمی است؛ ablation نهایی QSNN-v3 یا classical-head نیست |
| configs و وزن‌ها در درخت commit پیدا نشدند | بررسی مسیرهای `configs/`، `ResearchLoop/` و پسوندهای `.pt/.pth/.ckpt/.npz` در فایل‌های tracked | نبود در commit؛ به معنی نبود در کامپیوتر، فایل ignored یا محل دیگری نیست |

درخت default HEAD بررسی شد؛ دربارهٔ فایل‌های محلی، شاخه‌های دیگر یا ذخیره‌سازی بیرون Git ادعای نبودن نکن. هنگام اجرای Codex، وضعیت محلی ممکن است جدیدتر باشد و باید دوباره inventory شود.

## 3. داوری‌های عمده و اقدام اصلاحی

### R1 — شواهد test و تعمیم‌پذیری هنوز ناکافی است

**محل:** چکیده، صفحات ۱، ۴، ۵ و ۷.  
**مشاهده:** دقت پنج seed روی validation است؛ حمله روی ۱۰۰ نمونهٔ مشترک clean-correct و یک seed انجام شده است.  
**اهمیت:** مدل انتخاب‌شده با validation و چند failure محدود، برآورد مستقل robust test performance یا رفتار عمومی QSNN نیست.

**اقدام:** مطابق Phase 3، attack config روی development تثبیت و سپس clean test کامل و حملات روی manifest test از پیش مشخص اجرا شوند. هدف عملی اولیه ۱۰۰۰ نمونهٔ مشترک clean-correct و چند frontend مستقل است؛ عدد واقعی و محدودیت منابع گزارش شوند. سه یا پنج seed حد عمومی پذیرش نیست و استقلال frontend باید واقعی باشد.

**معیار رفع:** checkpoint/hash، config، manifest، رکورد هر نمونه، aggregate و هزینهٔ اجرا موجود؛ تفکیک test/validation و training/attack seeds روشن. اگر اجرا ممکن نیست، ادعا محدود و کار `blocked` ثبت شود؛ افزودن future work به‌تنهایی رفع R1 نیست.

### R2 — قانون انتخاب خروجی PGD باید اجرایی ممیزی شود

**محل:** صفحهٔ ۳، Timestamp PGD؛ `scripts/run_nmnist_common_attack_protocol_seed42.py`.  
**مشاهده:** خروجی maximum CE انتخاب می‌شود؛ ممکن است successful candidate میانی کنار گذاشته شود. متن فعلی درست می‌گوید که وقوع این اثر تأیید نشده است.

**اقدام:** روی دقیقاً همان candidateها، legacy selection و any-valid-success مقایسه شوند. TEMP هم با hard argmax و validity یکسان ارزیابی شود؛ margin صفر به‌تنهایی success نیست. trajectory search برای این مقایسه تغییر نکند. هزینهٔ audit و verification جدا ثبت شود.

**معیار رفع:** تعداد و ID مثال‌های دارای اختلاف selection، گام اولین موفقیت و ASR هر قانون موجود باشد. اختلاف صفر نیز نتیجهٔ معتبر است. نتایج تازه با برچسب مستقل ارائه شوند؛ اعداد تاریخی silent اصلاح نشوند.

### R3 — واحد forward و مقایسهٔ زمان باید دقیق شود

**محل:** صفحهٔ ۴، بخش 5.2 و Results.  
**مشاهده:** متن از ۴۱ forward برای PGD و Q forward برای TEMP صحبت می‌کند، درحالی‌که TEMP از chunk استفاده می‌کند. تعداد call، تعداد candidate و میزان کار محاسباتی یکسان نیستند.

**اقدام:** برای هر condition ثبت کن: candidate count، unique candidates، model invocations، sum of batch sizes، backward calls، verification calls، dtype، device، chunk و زمان. اصطلاح forward-equivalent فقط با تعریف عملی روشن استفاده شود. PGD برخی inputها را برای scoring و gradient دوباره ارزیابی می‌کند؛ این نکته در مقایسهٔ Q صریح باشد.

زمان‌سنجی تازه روی همان دستگاه، با warm-up و synchronization و raw timings انجام شود. batching فعلی به‌عنوان کارایی implementation گزارش شود؛ sensitivity محدود serial/chunk نیز روی pilot انجام گیرد. ratio زمان و پراکندگی آن ارائه شوند؛ backward با ضریب حدسی به forward تبدیل نشود.

**معیار رفع:** جدول هزینه از counterهای runner و raw timings ساخته شود. نبود snapshot سخت‌افزار تاریخی با اطلاعات دستگاه فعلی پر نشود.

### R4 — توضیح نبود کد baselineها باید اصلاح شود

**محل:** انتهای 5.2، صفحهٔ ۵؛ Discussion و Data availability صفحهٔ ۷.  
**مشاهده:** PDF می‌گوید exact baseline definitions غایب‌اند، ولی loader و سه فایل مرجع در مخزن وجود دارند.

**اقدام:** availability را به چهار سطح تفکیک کن: source موجود، config موجود/مفقود، checkpoint موجود/مفقود و linkage اجرای تاریخی. sourceها را به manifest شواهد اضافه و hash ثبت کن. از README منشأ upstream را دنبال کن؛ نسبت‌دادن به یک مقالهٔ معماری صرفاً با اسم ResNet انجام نشود.

**متن پیشنهادی جایگزین، پس از تطبیق با inventory محلی:**

```latex
The public source snapshot contains the controlled-model loader and reference model definitions. Exact reconstruction of the reported runs still requires the corresponding training configurations, checkpoints, manifests and their recorded hashes. Source availability therefore does not by itself establish that every historical result can be replayed.
```

**معیار رفع:** هیچ عبارت کلیِ ناسازگار با فایل‌های واقعاً موجود باقی نماند؛ وجود کد با reproduced result یکی نشود.

### R5 — نام ConvNet می‌تواند نوع baseline را مبهم کند

**محل:** شکل ۳، جدول ۳ و Related Work.  
**شاهد:** mapping `convnet -> SimpleNet_v2` و وجود `LIFNode` در SimpleNet_v2.

**اقدام:** در اولین معرفی بنویس `ConvNet (spiking SimpleNet_v2)`؛ label کوتاه تاریخی در شکل می‌تواند حفظ شود، به شرط تعریف روشن. میان classical به معنی non-quantum و conventional ANN تفاوت بگذار. این مدل را CNN دارای ReLU معرفی نکن؛ کلاس جداگانهٔ `SimpleNet_v2_CNN` انتخاب نشده است.

**معیار رفع:** جدول مدل‌ها شامل class، spiking/nonspiking، temporal aggregation، پارامترهای قابل تأیید و source hash باشد. شمارش پارامتر published reference را بدون تطبیق جای local victim ننشان.

### R6 — خطر test-dependent training gate باید بررسی و برای اجراهای تازه اصلاح شود

**شاهد:** `scripts/train_nmnist_controlled_four_models.py` در خطوط 74–79 از test accuracy برای skip/revise استفاده می‌کند؛ خطوط 143–156 status را با threshold 0.95 تعیین و دستور اصلاح recipe می‌دهند.

**اهمیت:** checkpoint هر run ممکن است validation-selected باشد، اما اگر recipe پس از دیدن test عوض شود، test دیگر ارزیابی کاملاً مستقل توسعه نیست. صرف دیدن این کد اثبات نمی‌کند که نتایج تاریخی آلوده‌اند.

**اقدام لازم:**

1. ترتیب زمانی configها، runها و test access با logs بررسی شود.
2. مشخص شود threshold از قبل فقط یک warning بود یا واقعاً باعث تغییر recipe/انتخاب run شد.
3. برای اجراهای تازه، توسعه و quality gate عملکردی روی validation باشد؛ test outcome صرفاً گزارش شود، نه مجوز تغییر recipe.
4. gateهای علمی validity، leakage، hash و audit حذف یا ضعیف نشوند. status اجرای صحیح با مطلوب‌بودن accuracy فرق داشته باشد.
5. اگر test برای توسعه مصرف شده، صریح گزارش شود. اجرای دوباره روی همان test مصرف‌شده استقلال را برنمی‌گرداند؛ به دادهٔ دست‌نخورده یا طرح ارزیابی بیرونی معتبر نیاز است، وگرنه محدودیت حفظ شود.

**معیار رفع:** گزارش `test_access_audit.md` با شواهد زمانی و اصلاح runner تازه؛ نبود شواهد به ادعای عدم leakage تبدیل نشود.

### R7 — نقش quantum head و ماهیت temporal representation هنوز جدا نشده است

**محل:** عنوان، contribution اول، بخش‌های 3.2 و 3.3 و Discussion.  
**مشاهده:** frontend کلاسیک آمار spike/membrane را خلاصه و سپس latent را به angles تبدیل می‌کند. مدار مستقیماً raw timestampها را به‌صورت یک quantum LIF network پردازش نمی‌کند.

**اقدام:** temporal information از frontend می‌آید؛ این موضوع یک‌بار روشن بیان شود. classical-head و no-entanglement ablation با frontend/split/training ثابت روی مدل نهایی اجرا شوند. ablation قدیمی با 154 تا 274 پارامتر و خروجی local Pauli-Z را ablation مدل 40,762پارامتری با 256 probability معرفی نکن.

اگر ablation ممکن نیست، عنوان/سهم کار در حد مطالعهٔ تجربی end-to-end نگه داشته شود. ادعای مکانیزم اختصاصی یا quantum advantage ایجاد نشود.

**معیار رفع:** نتیجهٔ کنترل‌شده با هزینه و عدم‌قطعیت یا narrowing روشن ادعا؛ صرف توضیح بیشتر در Introduction جای آزمایش نیست.

### R8 — اختلاف بزرگ grid و تنظیمات B0 نیازمند توضیح است

**محل:** صفحات ۴–۷ و شکل ۳.  
**مشاهده:** ASR حدود 98–100٪ برای custom و 0–1.9٪ برای کنترل‌ها؛ report از اختلاف penalty پنج و ده می‌گوید.

**اقدام:**

- کد adapter موجود را تا constructor upstream و defaults آن دنبال کن؛ runtime resolved parameters و source hash ثبت شود.
- در B0 adapter، `lambda_cap=20` دیده می‌شود؛ این را با ضریب penalty مورد بحث یکی فرض نکن.
- `surrogate.PiecewiseLeakyReLU(c=0.0)` در مدل‌های مرجع وجود دارد. این مشاهده به‌تنهایی gradient masking را اثبات نمی‌کند؛ gradient coverage، alternative surrogate و search strength با hard-forward verification بررسی شوند.
- resetهای موجود را در مقاله به‌عنوان static source evidence ثبت و آزمایش batching/order/reset را اجرا کن.
- baseline و custom attack روی config یکسان لزوماً قدرت برابر ندارند. قبل از causal architecture ranking، این تمایز باقی بماند.

**معیار رفع:** resolved config و audit اجرایی. اگر raw artifacts پیدا نشدند، جدول در نقش historical/contextual باقی بماند؛ عددی از مقالهٔ مرجع برای کامل‌کردن result cells وارد نشود.

## 4. اصلاح‌های آماری، ریاضی و نگارشی باقی‌مانده

| ID | مورد | اصلاح و معیار بررسی |
|---|---|---|
| M1 | 97.2720 و SD با اعشار زیاد | در متن اصلی معمولاً 97.27 ± 0.21٪ کافی است؛ مقدار دقیق در data/supplement حفظ شود؛ خطای rounding ایجاد نشود |
| M2 | Wilson روی subset انتخاب‌شده | ماهیت descriptive/model-based حفظ شود؛ interval را uncertainty کل test یا paired difference ننام |
| M3 | exact McNemar و نمونه‌های تکراری | جدول discordance مبنا باشد؛ بین شروط/seedهای تکراری استقلال مصنوعی ایجاد نشود؛ formula exact در supplement روشن بماند |
| M4 | claim «matching changes comparison» | با قید numerical روی همین جمعیت بیان شود؛ اختلاف دو نمونه را تغییر نتیجهٔ آماری یا اثبات causal ننام |
| M5 | state–margin bound | شرط کافیِ readout ثابت است؛ certified timestamp radius یا نظریهٔ بنیادی تازه معرفی نشود |
| M6 | p برای polarity و probability، y برای مختصات/label | جدول notation کوتاه؛ event polarity و probability vector و class label متمایز شوند |
| M7 | روش hard-forward/soft-backward | feasibility operator و surrogate دقیق؛ finite-difference صفر داخل bin را خودکار bug ننام |
| M8 | TEMP در شعاع ۱۰٪ از ۵٪ ضعیف‌تر می‌شود | finite-search effect ممکن است؛ standalone و cumulative جدا، هزینهٔ warm start ثبت شود |
| M9 | تعداد candidate با rounded budget | requested و actual Q هر دو؛ از نسبت‌دادن warm-up 400 به 400 proposal واقعی اجتناب شود اگر schedule 398 تولید می‌کند |
| M10 | تکرار limitations در Related Work/Discussion | هر تفاوت روش یک‌بار در پیشینه؛ حدود شواهد در بخش متمرکز؛ جملهٔ «not our defense» برای هر reference تکرار نشود |
| M11 | منابع شکسته در مرز صفحه | URL داخل bibliography با line break مناسب؛ DOI/eprint استاندارد، نه noteهای طولانی |
| M12 | attribution auditهای تاریخی | PASS گزارش‌شده از independently rerun در این نسخه جدا باشد |
| M13 | availability کلی | ماتریس source/config/weights/data/results/audit و دستور بازتولید حداقلی؛ READMEهای متناقض اصلاح یا تاریخ‌دار شوند |

اعداد منبع، seed، مخرج، snapshot و p-value بدون شواهد جدید تغییر نکنند. تغییر نگارشی به تغییر تجربی تبدیل نشود.

## 5. گسترش هدفمند منابع: ۱۲ مدخل افزوده

نسخهٔ فعلی ۲۰ مدخل دارد. این فاز ۱۲ منبع افزوده با کاربرد مشخص پیشنهاد می‌کند؛ با افزودن همهٔ مواردِ واقعاً استفاده‌شده و نبود duplicate، شمار bibliography به ۳۲ می‌رسد. این هدف ویرایشی است، نه حد پذیرش. برای رسیدن به عدد، `nocite{*}` یا citation نامرتبط اضافه نکن.

چهار مورد 2024–2026 هستند؛ بقیه منابع بنیادی روش/نظریه‌اند. «جدید برای bibliography» به معنی «همگی تازه‌منتشرشده» نیست. BibTeX زیر از عنوان و metadata منابع اصلی/رکورد نویسندگان تهیه شده؛ ادعاهای جزئی‌تر نیازمند خواندن متن کامل همان نسخه‌اند.

| کلید | کاربرد دقیق | حدود ادعا و منبع |
|---|---|---|
| `lun2025surrogate` | surrogateهای ناشناخته و حمله به SNN، Related Work و search diagnostics | PDSG/SDA؛ معادل retiming-only نیست. [CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Lun_Towards_Effective_and_Sparse_Adversarial_Attack_on_Spiking_Neural_Networks_CVPR_2025_paper.html)، [نسخهٔ نویسندگان](https://arxiv.org/abs/2503.03272) |
| `wang2026rte` | temporal structure و robust training در SNN | دفاع آموزش‌محور، نه اثبات حفاظت در feasible set ما. [AAAI 2026، 40(31):26285–26293](https://ojs.aaai.org/index.php/AAAI/article/view/39833) |
| `schmolli2025sparse` | تفاوت architecture/training و robustness در SNN | robust ANN-to-SNN conversion و sparsity؛ نتیجهٔ محلی مقالهٔ ما نیست. [PMLR 280:865–883](https://proceedings.mlr.press/v280/schmolli25a.html) |
| `saxena2024encoding` | فاصلهٔ ادعای robustness در classical input و quantum state | assumptions encoding/noise لازم‌اند؛ به QSNN-v3 certificate نمی‌دهد. [QCE/نسخهٔ نویسندگان](https://arxiv.org/abs/2408.01200)، [DOI](https://doi.org/10.1109/QCE60285.2024.00184) |
| `lu2020quantumadv` | زمینهٔ بنیادی حمله به quantum classifiers | quantum و classical input scenarios؛ اثبات مکانیزم retiming فعلی نیست. [PRR 2,033212](https://doi.org/10.1103/PhysRevResearch.2.033212) |
| `liu2020vulnerability` | وابستگی تهدید کوانتومی به هندسه و assumptions | نتیجهٔ high-dimensional setting را به مدار هشت‌کیوبیتی دلخواه تعمیم نده. [PRA 101,062331](https://doi.org/10.1103/PhysRevA.101.062331) |
| `schuld2021encoding` | encoding/re-uploading و expressive power | expressive power با robustness یا advantage یکی نیست. [PRA 103,032430](https://doi.org/10.1103/PhysRevA.103.032430) |
| `ilyas2018queries` | تفکیک query-limited، score-based و label-only access | TEMP logits می‌خواهد؛ label-only نیست. [ICML/PMLR 80:2137–2146](https://proceedings.mlr.press/v80/ilyas18a.html) |
| `andriushchenko2020square` | سابقهٔ derivative-free random search و query efficiency | Square Attack تصویرمحور است؛ اجرای مستقیم آن در raw event space گزارش نشود. [ECCV paper](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123680477.pdf) |
| `tramer2020adaptive` | ضرورت attack adaptation و diagnostics | مقالهٔ حاضر defense benchmark نیست؛ ارجاع برای روش ارزیابی است. [NeurIPS 2020](https://proceedings.neurips.cc/paper_files/paper/2020/hash/11f38f8ecd71867b42433548d1078e38-Abstract.html) |
| `wilson1927` | interval استفاده‌شده در شکل ۲ | منبع score interval؛ selection bias یا طراحی نمونه‌گیری را اصلاح نمی‌کند. [ناشر](https://doi.org/10.1080/01621459.1927.10502953)، [نسخهٔ مقاله](https://www.jhanley.biostat.mcgill.ca/c607/ch08/wilson_jasa_1927.pdf) |
| `mcnemar1947` | سابقهٔ آزمون paired proportions | منبع بنیادی؛ exact binomial implementation و conventionهای فعلی جدا تعریف شوند. [Psychometrika 12:153–157](https://link.springer.com/article/10.1007/BF02295996) |

### 5.1 متن آماده برای ادغام در Related Work

این پاراگراف‌ها جایگزین/تکمیل بخش‌های متناظر شوند، نه اینکه بدون حذف تکرار به انتهای متن الصاق شوند.

```latex
\paragraph{Surrogate choice and temporal robustness in SNNs.}
Attack effectiveness in spiking models depends on how the backward approximation relates to the evaluated forward model. Lun et al. study attacks with inference-invisible surrogate gradients and introduce potential-dependent surrogates and sparse attacks \cite{lun2025surrogate}. Separately, robust temporal self-ensembling \cite{wang2026rte} and robust sparse ANN-to-SNN conversion \cite{schmolli2025sparse} examine how training and model construction affect adversarial behavior. These studies motivate architecture-aware optimization diagnostics, while their perturbation sets and training interventions differ from our timing-only evaluation.

\paragraph{Adversarial access and derivative-free search.}
Query-limited, partial-information and label-only adversaries expose different interfaces \cite{ilyas2018queries}. TEMP-DRIFT-v2 uses score information through the class logits and does not require backward gradients; it is therefore not a label-only attack. Score-based random search has established precedents, including Square Attack \cite{andriushchenko2020square}. Our evaluation concerns feasible timestamp proposals, so image-space proposal rules and their performance cannot be transferred directly. Adaptive evaluation further motivates testing optimization choices against the implemented pipeline rather than treating one optimizer's failure as a certificate \cite{tramer2020adaptive}.

\paragraph{Quantum vulnerability, encoding and guarantees.}
Quantum adversarial learning studies vulnerabilities under both classical and quantum input manipulations \cite{lu2020quantumadv}, with high-dimensional analyses emphasizing the importance of the threat model and state-space geometry \cite{liu2020vulnerability}. Encoding gates and their repetition also determine aspects of a variational model's expressive power \cite{schuld2021encoding}. Certification for perturbations of classical data requires additional assumptions linking the input, encoding and classifier, as illustrated by certifiably robust encoding schemes \cite{saxena2024encoding}. In our composition, that link additionally passes through temporal aggregation and a classical spiking frontend; the readout-specific margin bound alone does not establish an event-retiming certificate.
```

در Metrics به جمله‌های موجود، citation مناسب اضافه کن:

```latex
We summarize the reported success counts using Wilson score intervals \cite{wilson1927} and paired attack discordances using the McNemar framework \cite{mcnemar1947}. For the latter, we explicitly use the two-sided conditional binomial calculation stated in the supplement. The marginal intervals are not intervals for the paired difference and do not remove the limitations of the selected attack population.
```

از تأیید روش exact توسط صرف citation تاریخی برداشت نکن؛ formula و محاسبه باید خودشان روشن و قابل بررسی باشند.

### 5.2 BibTeX آماده

قبل از درج، عنوان و DOI با bibliography محلی مقایسه شوند. اگر منبع از قبل وجود دارد، کلید موجود را reuse کن و duplicate نساز. مشخصات صفحات/DOI نامعلوم عمداً حذف شده‌اند؛ حدس نزن.

```bibtex
@inproceedings{lun2025surrogate,
  author = {Lun, Li and Feng, Kunyu and Ni, Qinglong and Liang, Ling and Wang, Yuan and Li, Ying and Yu, Dunshan and Cui, Xiaoxin},
  title = {Towards Effective and Sparse Adversarial Attack on Spiking Neural Networks via Breaking Invisible Surrogate Gradients},
  booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  pages = {3540--3551},
  year = {2025},
  url = {https://arxiv.org/abs/2503.03272}
}

@article{wang2026rte,
  author = {Wang, Jihang and Zhao, Dongcheng and Chen, Ruolin and Zhang, Qian and Zeng, Yi},
  title = {Boosting the Robustness-Accuracy Trade-off of {SNNs} by Robust Temporal Self-Ensemble},
  journal = {Proceedings of the AAAI Conference on Artificial Intelligence},
  volume = {40},
  number = {31},
  pages = {26285--26293},
  year = {2026},
  doi = {10.1609/aaai.v40i31.39833},
  url = {https://ojs.aaai.org/index.php/AAAI/article/view/39833}
}

@inproceedings{schmolli2025sparse,
  author = {Schmolli, Mathias and Baronig, Maximilian and Legenstein, Robert and Ozdenizci, Ozan},
  title = {Adversarially Robust Spiking Neural Networks with Sparse Connectivity},
  booktitle = {Conference on Parsimony and Learning},
  series = {Proceedings of Machine Learning Research},
  volume = {280},
  pages = {865--883},
  year = {2025},
  publisher = {PMLR},
  url = {https://proceedings.mlr.press/v280/schmolli25a.html}
}

@inproceedings{saxena2024encoding,
  author = {Saxena, Aman and Wollschl{\"a}ger, Tom and Franco, Nicola and Lorenz, Jeanette Miriam and G{\"u}nnemann, Stephan},
  title = {Certifiably Robust Encoding Schemes},
  booktitle = {2024 IEEE International Conference on Quantum Computing and Engineering (QCE)},
  year = {2024},
  doi = {10.1109/QCE60285.2024.00184},
  url = {https://arxiv.org/abs/2408.01200}
}

@article{lu2020quantumadv,
  author = {Lu, Sirui and Duan, Lu-Ming and Deng, Dong-Ling},
  title = {Quantum adversarial machine learning},
  journal = {Physical Review Research},
  volume = {2},
  pages = {033212},
  year = {2020},
  doi = {10.1103/PhysRevResearch.2.033212}
}

@article{liu2020vulnerability,
  author = {Liu, Nana and Wittek, Peter},
  title = {Vulnerability of quantum classification to adversarial perturbations},
  journal = {Physical Review A},
  volume = {101},
  pages = {062331},
  year = {2020},
  doi = {10.1103/PhysRevA.101.062331}
}

@article{schuld2021encoding,
  author = {Schuld, Maria and Sweke, Ryan and Meyer, Johannes Jakob},
  title = {Effect of data encoding on the expressive power of variational quantum-machine-learning models},
  journal = {Physical Review A},
  volume = {103},
  pages = {032430},
  year = {2021},
  doi = {10.1103/PhysRevA.103.032430}
}

@inproceedings{ilyas2018queries,
  author = {Ilyas, Andrew and Engstrom, Logan and Athalye, Anish and Lin, Jessy},
  title = {Black-box Adversarial Attacks with Limited Queries and Information},
  booktitle = {Proceedings of the 35th International Conference on Machine Learning},
  series = {Proceedings of Machine Learning Research},
  volume = {80},
  pages = {2137--2146},
  year = {2018},
  publisher = {PMLR},
  url = {https://proceedings.mlr.press/v80/ilyas18a.html}
}

@inproceedings{andriushchenko2020square,
  author = {Andriushchenko, Maksym and Croce, Francesco and Flammarion, Nicolas and Hein, Matthias},
  title = {Square Attack: A Query-Efficient Black-Box Adversarial Attack via Random Search},
  booktitle = {Computer Vision -- ECCV 2020},
  year = {2020},
  url = {https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123680477.pdf}
}

@inproceedings{tramer2020adaptive,
  author = {Tram{\`e}r, Florian and Carlini, Nicholas and Brendel, Wieland and Madry, Aleksander},
  title = {On Adaptive Attacks to Adversarial Example Defenses},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {33},
  year = {2020},
  url = {https://proceedings.neurips.cc/paper_files/paper/2020/hash/11f38f8ecd71867b42433548d1078e38-Abstract.html}
}

@article{wilson1927,
  author = {Wilson, Edwin B.},
  title = {Probable Inference, the Law of Succession, and Statistical Inference},
  journal = {Journal of the American Statistical Association},
  volume = {22},
  number = {158},
  pages = {209--212},
  year = {1927},
  doi = {10.1080/01621459.1927.10502953}
}

@article{mcnemar1947,
  author = {McNemar, Quinn},
  title = {Note on the sampling error of the difference between correlated proportions or percentages},
  journal = {Psychometrika},
  volume = {12},
  pages = {153--157},
  year = {1947},
  doi = {10.1007/BF02295996}
}
```

### 5.3 کیفیت bibliography نهایی

- DOI و arXiv یک اثر دو مدخل جدا نشوند؛ RTE با نسخهٔ AAAI 2026 ارجاع شود، نه دو بار با preprint 2025.
- Liu/Wittek نسخهٔ ژورنالی **2020، جلد 101** است؛ سال preprint 2019 با جلد/سال ژورنال مخلوط نشود.
- منابع قبلی Yu، SPATE، Brand، Watrous، Büchel و Khatun دوباره اضافه نشوند.
- frozen v1 پروتکل Yu و commit شواهد حفظ شوند.
- cite کردن Fang/SEW صرفاً به خاطر عبارت ResNet18 ممنوع است؛ ابتدا تطبیق implementation.
- citationها بین Introduction، Related Work، Methods/Statistics و Discussion توزیع شوند؛ پاراگراف انبوه نام‌ها بدون استدلال ساخته نشود.
- برای هر منبع ledger شامل key، DOI/URL، سال، نوع انتشار، محل استناد و ادعای پشتیبانی‌شده ثبت شود.
- طول مقاله با حذف تکرار کنترل شود؛ برای جا دادن منابع فونت غیرعادی کوچک نشود و محدودیت venue واقعی بررسی شود.

## 6. اصلاح شکل‌ها: محتوا و خوانایی

### شکل ۱ — صفحهٔ ۳

ساختار فعلی حفظ شود، مگر اینکه خوانایی چاپ نیاز به تفکیک داشته باشد. gate labels کوچک‌اند؛ بزرگ‌کردن فونت یا انتقال مدار کامل به supplement بر ریزکردن بیشتر اولویت دارد. label عمومی i با wireهای q0 تا q7 سازگار تعریف شود. متغیرهای trainable، fixed-at-inference و input-dependent در legend کوتاه تفکیک شوند. هیچ نمودار مدار، شواهد attack example محسوب نشود.

### شکل ۲ — صفحهٔ ۶

نمایش paired counts جدید مناسب‌تر است. توضیح ادغام candidate/forward یک‌بار در caption کافی است؛ متن طولانی زیر محور حذف یا کوتاه شود. در main یک جدول کوچک هزینه کنار شکل/در Protocol بیاور تا معلوم باشد شمارش یکسان، بودجهٔ یکسان نیست. paired difference با CI از overlap بازه‌های Wilson نتیجه‌گیری نشود.

### شکل ۳ — صفحهٔ ۷

نام baseline طبق R5 روشن شود. labelهای inset فاصلهٔ کافی داشته باشند؛ کل نمودار در اندازهٔ واقعی چاپ و grayscale بررسی شود. این شکل historical/contextual بماند تا provenance و قدرت حمله تأیید شوند. در صورت محدودیت صفحه، controlهای grid می‌توانند به supplement منتقل شوند، اما نتیجهٔ اصلی QSNN و جزئیات بودجه در main بمانند.

### شکل‌های جدید فقط با نتیجهٔ واقعی

ترتیب ارزش علمی:

1. **ASR در برابر actual candidates/elapsed time** با best-so-far، چند attack seed و هزینهٔ روشن.
2. **یک exemplar واقعی clean/retimed**: raw timing، realized displacement، bin-count changes و logits همان نمونه.
3. **classical-head/no-entangler ablation** یا **state–margin** در مدل نهایی.

انتخاب exemplar با rule ثبت‌شده، نه فقط زیباترین نمونه. نمودار با دادهٔ فرضی، interpolation نمایشی بین budgetهای اجرا‌نشده یا تصویر مولد برای chart/circuit دقیق تولید نشود. سه شکل قوی کافی‌اند؛ تعداد بیشتر به خودی خود ارزش علمی ندارد.

## 7. بستن کارهای باز Phase 3 بدون شروع دوباره

ابتدا `Reports/phase3/`، محل معادل آن و تغییرهای محلی را بخوان. وجود اسکریپت برابر اجرای آزمایش نیست. اگر گزارش completion با artifact/hash و auditor معتبر موجود است، آن واحد دوباره اجرا نشود.

| واحد | خروجی لازم | وضعیت پیش‌فرض تا بررسی محلی |
|---|---|---|
| P0 | inventory، محیط، smoke/pilot و source hashes | در PDF جدید اثبات نشده |
| P1 | selection audit اجرایی و per-candidate hard outcomes | در PDF جدید اثبات نشده |
| P2 | attack-strength sweep روی development، config نهایی ثابت | در PDF جدید اثبات نشده |
| P3 | official-test clean/attack، manifest و seedهای مستقل | در PDF صریحاً انجام‌نشده |
| P4 | head/circuit ablation مدل نهایی | در PDF صریحاً انجام‌نشده |
| P5 | exemplar و state/probability/margin هر نمونه | شواهد مدل نهایی در PDF موجود نیست |

اگر checkpoint تاریخی غایب و train code/data حاضر است، اجرای تازه با run ID/config جدید مجاز است؛ آن را replay دقیقِ وزن تاریخی ننام. اگر grid مسدود است ولی QSNN قابل اجراست، مطالعهٔ اصلی ادامه یابد.

از Phase 3 این قواعد حفظ شوند: تنظیم روی development پیش از test، هزینهٔ pilot واقعی، resume، ذخیرهٔ مخرج و ID، عدم pool سادهٔ نمونه‌های تکراری، validation-only model selection و عدم هدف‌گذاری ASR/p-value مطلوب.

## 8. اصلاح مسیر اجرا و بستهٔ بازتولید

چند runner مخزن به interpreter ویندوزی hardcoded وابسته‌اند. در همان checkout بررسی کن آیا `ResearchLoop/config.json` و contracts واقعاً موجودند؛ این مسیرها در AGENTS ارجاع داده شده‌اند ولی در commit بررسی‌شده tracked نبودند.

- اگر interpreter قراردادی در محیط محلی وجود دارد، همان استفاده شود.
- اگر فایل/مسیر تاریخی وجود ندارد، مسیر portable صریح برای اجرای تازه طراحی و انتخاب واقعی interpreter در report ثبت شود؛ از جعل وجود فایل config یا وانمودکردن اجرا با مسیر تاریخی اجتناب شود.
- تغییر عملیاتیِ مسیر نباید scientific settings، invariant، budget یا audit gate را ضعیف کند.
- README بازتولید باید dependency نسخه‌دار، مسیر داده، دانلود مجاز dataset، checkpoint/config موردنیاز و command کوچک smoke run داشته باشد.
- imports و executable بودن یک runner بدون data/checkpoint، reproduction نیست.

source-only package، runtime-only artifact و manuscript LaTeX ممکن است در پوشه/مخزنهای جدا باشند. ریشه‌ها را صریح resolve کن؛ اسکریپت‌های paper و benchmark در مقصد اشتباه نوشته نشوند. شمارهٔ Phase 4 این فایل مربوط به **manuscript revision** است و نباید بدون بررسی با phase شمارهٔ ۴ ResearchLoop یکسان فرض شود.

## 9. ترتیب اجرا و فایل‌های تحویل

### بستهٔ A — اصلاح‌های فوری

1. خواندن وضعیت محلی و sourceهای R4–R8؛ ثبت commit و تفاوت با این داوری.
2. اصلاح availability و نام baseline در main/supplement/figure labels.
3. تکمیل ۱۲ reference و ادغام متن‌های آماده؛ citation audit و duplicate check.
4. اصلاح واحد هزینه، notation و نگارش؛ captionهای کوتاه‌تر و خوانایی شکل‌ها.
5. ارائهٔ diff و build جدید؛ هیچ عبارت «آزمایش تازه انجام شد» بدون خروجی معتبر اضافه نشود.

### بستهٔ B — ممیزی و اصلاح اجرایی

1. ممیزی test-access gate؛ ثبت آنچه از history معلوم/نامعلوم است.
2. اجرای candidate selection audit، validity/reset checks و resolved-budget counters.
3. بررسی defaults upstream برای B0 و linkage کد/گزارش.
4. تکمیل کوچک‌ترین واحدهای باقی‌ماندهٔ Phase 3؛ سپس test و ablation متناسب با منابع.

### بستهٔ C — انتشار داخلی نتایج و پاسخ به داوری

ساختار پیشنهادی، با رعایت قرارداد مسیرهای مخزن:

```text
Reports/manuscript_phase4/
  peer_review.md
  response_to_review.md
  claim_evidence.csv
  citation_ledger.csv
  repository_availability.json
  test_access_audit.md
  selection_audit.json
  compute_accounting.csv
  execution_status.json
  verification.json
  remaining_work.md
Reports/results/manuscript_phase4/
Reports/logs/manuscript_phase4/
Reports/checkpoints/manuscript_phase4/
```

این مسیرها پیشنهادند؛ خروجی معادل معتبر را صرفاً برای تغییر نام duplicate نکن. هر ردیف پاسخ داوری شامل `comment_id, action, changed_files, evidence, status, remaining_limit` باشد.

## 10. بررسی نهایی و معیار واقعی پایان

### کنترل علمی

- [ ] هر ادعای عددی با result artifact و population مطابقت دارد.
- [ ] نتیجهٔ report-only با اجرا و audit مستقل یکی نشده است.
- [ ] بحث test-dependent gate با evidence یا limitation بسته شده است.
- [ ] candidate selection، actual budget و هزینهٔ verification روشن‌اند.
- [ ] test و ablation جدید یا واقعاً اجرا شده‌اند یا صریحاً باز مانده‌اند.
- [ ] clean accuracy، ASR و survival با مخرج‌های متفاوت مخلوط نشده‌اند.
- [ ] نبود اختلاف معنادار به equivalence یا superiority تبدیل نشده است.

### کنترل منابع و PDF

- [ ] هر یک از ۱۲ منبع افزوده یا واقعاً استناد شده یا با دلیل کنار گذاشته شده است؛ شمارش واقعی گزارش شده است.
- [ ] duplicate DOI/title و citation undefined وجود ندارد؛ ارجاع‌های موجود حفظ شده‌اند.
- [ ] main/supplement با backend موجود کامپایل شده‌اند؛ error، overflow مهم و broken reference بررسی شده‌اند.
- [ ] شکل‌ها در اندازهٔ واقعی، چاپ خاکستری و خروجی vector بررسی شده‌اند.
- [ ] تمام source-dataهای شکل/جدول به نتیجهٔ ماشینی متصل‌اند؛ هیچ دادهٔ ساختگی وارد نشده است.

### وضعیت پایان

برای هر R و M یکی از `resolved`، `partially_resolved`، `open` یا `blocked` همراه شاهد ثبت شود. کتابنامهٔ کامل یا build موفق R1/R2/R6/R7 را به‌تنهایی resolved نمی‌کند. اگر آزمایش‌ها اجرا نشدند، گزارش فقط «اصلاح ویرایشی/منابع تکمیل شد؛ اعتبارسنجی تجربی باز است» باشد.

این فاز مجوز تغییر نتایج تاریخی، حذف دادهٔ نامطلوب یا تضمین پذیرش نیست. هیچ push/commit/ارسال مقاله یا تغییر Overleaf در این دستور درخواست نشده است.

## 11. دستور آماده برای Codex

> phase4.md را کامل بخوان و ابتدا دستورهای پروژه، وضعیت محلی و نتایج واقعی Phase 3 را بررسی کن. این فایل را ادامهٔ manuscript revision بدان، نه شمارهٔ phase آزمایش‌های ResearchLoop. داوری‌های R1 تا R8 و M1 تا M13 را به فهرست قابل پیگیری تبدیل کن. sourceهای baseline و gate وابسته به test را بررسی و ادعاهای نادرست availability را اصلاح کن؛ وجود کد را با موجودبودن checkpoint و اجرای تاریخی یکی ندان. ۱۲ منبع پیشنهادی را با bibliography فعلی merge و متن‌های آماده را بدون تکرار در جای درست ادغام کن. کارهای اجراییِ ممکن را با حفظ داده‌های تاریخی و واحدهای کامل‌شدهٔ معتبر ادامه بده؛ selection audit و هزینهٔ واقعی اولویت دارند. تنظیمات حمله روی development ثابت و test برای انتخاب recipe مصرف نشود. فقط دادهٔ اجراشده و قابل تأیید وارد مقاله و شکل‌ها شود. برای هر مورد response با فایل، شاهد و وضعیت بنویس. main و supplement را build و PDF را بصری بررسی کن. در پایان تعداد واقعی منابع، یافته‌های ممیزی، آزمایش‌های completed/blocked و موارد حل‌نشده را صریح گزارش کن؛ صرف تولید script یا PDF را تکمیل علمی همهٔ فاز معرفی نکن.
