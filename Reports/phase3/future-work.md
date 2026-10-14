# کارهای آیندهٔ Phase 3

کاربر در ۱۴ اکتبر ۲۰۲۶ تأیید کرد checkpointها و دادهٔ N-MNIST روی این سیستم موجود نیستند و اجرای وابسته به آن‌ها باید به آینده منتقل شود. **Phase 3 تجربی کامل نشده است.** موردهای زیر نتیجهٔ صفر یا شکست حمله محسوب نمی‌شوند.

| ترتیب | کار باقی‌مانده | پیش‌نیاز | معیار اتمام واقعی |
|---|---|---|---|
| ۱ — P0 | فراهم‌کردن artifactها و اجرای pilot واقعی | checkpoint صحیح frontend/QSNN/SNN، دادهٔ خام، split و manifest یا منشأ مستند manifest تازه | load با hash و state_dict صحیح، clean prediction، backward، candidate معتبر و hard verification؛ زمان و حافظهٔ اندازه‌گیری‌شده |
| ۲ — P1 | selection audit روی مدل آموزش‌دیده | مورد ۱ و candidateهای یکسان | legacy، any-valid-success و success-priority از یک بانک logits تأییدشده؛ تعداد اختلاف واقعی و ID/گام اولین موفقیت |
| ۳ — P2 | tuning مرحله‌ای روی validation | manifest development ثابت و stratified | steps/step size/restarts/CE/margin، TEMP چند seed و حداقل مقایسهٔ loss-matched؛ انتخاب بر اساس validation و هزینه |
| ۴ — P2 | calibration و chunk sensitivity | pilot و دستگاه/precision نهایی | warm-up و synchronization، median/IQR، actual Q و calls/equivalents؛ chunkهای ۱/۸/۶۴ فقط روی pilot |
| ۵ — P3 | تثبیت preregistration سپس official test | خروجی معتبر validation، hash config/source/dataset | clean روی تمام ۱۰هزار test؛ هدف اولیهٔ حمله ۱۰۰۰ joint clean-correct با sampling ثابت، مخرج/shortage روشن |
| ۶ — P3 | pipelineهای مستقل | داده، بودجهٔ training و حداقل سه frontend مستقل پیشنهادی | نتایج جداگانهٔ seedهای ۴۲/۱۲۳/۷۷۷؛ چند head روی یک frontend، چند pipeline مستقل نامیده نشود |
| ۷ — P4 | training و ablation واقعی headها | frontend ثابتِ تأییدشده، split یکسان و training runner کامل | Q کامل، head کلاسیک و Q بدون entangler با retraining و هزینهٔ برابرِ ثبت‌شده؛ constructor فعلی نتیجهٔ ablation نیست |
| ۸ — P5 | exemplar و state–margin واقعی | raw timestamps، logits/probabilities/statevectors هر نمونه | انتخاب exemplar با rule ثابت؛ TV/trace-distance و bound برای failure و survivor، بدون دادهٔ فرضی |
| بعدی | grid و monitor | artifact/configهای جداگانه | حل ضریب تاریخی B0 با سند؛ اجرای تازه جای حدس تاریخی ننشیند. monitor پس از تعریف observable/shot/calibration و adaptive attack |

## فایل‌های مورد نیاز برای ادامه

مسیرهای زیر ارجاع‌های واقعی runner تاریخی هستند، **نه فایل‌های موجود در این دستگاه**:

- `checkpoints/nmnist_hybrid_qsnn_seed42/v3_wide4_classical_full_best.pt`
- `checkpoints/nmnist_hybrid_qsnn_seed42/nmnist_qsnn_v3_multiseed/seed42_best.pt`
- `checkpoints/nmnist_snn_clean_seed42_best.pt`
- `results/nmnist_snn_multiseed_split.json`
- `results/nmnist_attack_protocol_v3_auditable_seed42/common_clean_correct_manifest.json`
- `results/nmnist_budget_matched_comparison_v2_seed42/{budget_definitions,wallclock_calibration}.json`
- دادهٔ خام N-MNIST و خروجی‌های هر نمونه، candidate trajectory و اطلاعات محیط تاریخی در صورت بازیابی.

نبود checkpoint با seed بازسازی نمی‌شود. اگر checkpoint موجود شد ولی manifest تاریخی بازیابی نشد، manifest تازه بسازید و نتیجه را `new_experiment` بنامید؛ نام `replayed` تنها برای replay مستند روی manifest اصلی مناسب است.

## نقطهٔ شروع عملی

۱. مسیر و SHA-256 فایل‌های واقعی را در **یک کپی** از `configs/phase3/pilot.yaml` پر کنید. sidecar metadata باید از شواهد واقعی checkpoint/config تهیه شود؛ template در همان پوشه است.

۲. exporter داده، dataset version و split IDs را تأیید و manifest جداگانهٔ pilot را تثبیت کنید. schema خام و دستورها در [راهنمای runner](../../scripts/phase3/README.md) آمده است.

۳. سپس این ترتیب را اجرا کنید:

```bash
python -m scripts.phase3.runner inventory
python -m scripts.phase3.runner pilot --config <resolved-pilot.yaml>
python -m scripts.phase3.runner attack --config <resolved-validation-condition.yaml>
```

۴. پس از pilot، ETA را از زمان واقعی همان condition بسازید. هزینهٔ test، training و time calibration را از سرعت unit test یا نسبت‌های تاریخی تخمین نزنید.

۵. preregistration فعلی عمداً `draft` است. بدون نتایج واقعی development آن را frozen نکنید. runner آماده، sweep خودکار، training campaign، calibration یا آزمایش انجام‌شده محسوب نمی‌شود؛ این بخش‌ها در نوبت بعد باید تکمیل و اجرا شوند.
