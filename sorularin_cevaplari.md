# VILAGENT Projesi - Sorular ve Detaylı Cevaplar

Bu doküman, VILAGENT projesinin mimarisi, çalışma prensipleri ve geliştirme olanakları hakkında sıkça sorulan teknik soruların detaylı cevaplarını içerir.

---

## 1. Prompt Yapısı Nasıl?

**Cevap:**
VILAGENT'ın kullandığı prompt yapısı dinamik bir şablona dayanır ve `src/utils/prompt_loader.py` modülü tarafından her döngüde (step) yeniden oluşturulur. Promptun ana bileşenleri şunlardır:

*   **Sistem Kimliği (System Identity):** Ajanın kim olduğunu ve amacını tanımlar (Örn: "Sen VILAGENT isminde, zeki bir Windows otomasyon asistanısın...").
*   **Stratejiler ve İpuçları (Strategies):** Windows otomasyonu için en iyi pratikleri içerir. Örneğin, "Uygulama açmak için ikon aramak yerine Başlat menüsünü (Win tuşu) kullan" gibi talimatlar burada yer alır. Bu, ajanın hata yapma oranını düşürür.
*   **Mevcut Hedef (Goal):** Kullanıcının o an talep ettiği görevdir (Örn: "WhatsApp'ı aç ve mesaj at").
*   **Bağlam (Context/RAG):** Pinecone vektör veritabanından çekilen, geçmişteki benzer görevlerin başarı hikayeleridir. Bu sayede ajan tekerleği yeniden icat etmez.
*   **Araç Tanımları (Tools Schema):** Ajanın kullanabileceği fonksiyonların (`execute_python`, `write_file` vb.) JSON formatındaki açıklamalarıdır.
*   **Ekran Görüntüsü (Multimodal Input):** Gemini modeline gönderilen anlık ekran görüntüsü verisidir.
*   **Görev Geçmişi (History):** Ajanın o ana kadar attığı adımların ("Thought" ve "Action") listesidir. Bu, ajanın döngüye girmesini engeller.

---

## 2. Prompt İçine OmniParser'dan Gelen Ekran Görüntüsü ve PyWinAuto'dan Gelen UI Ağacı Geliyor mu?

**Cevap:**

*   **OmniParser:** Mevcut prototip sürümünde, tam bir OmniParser entegrasyonu **bulunmamaktadır**. Şu an için `pyautogui` ile alınan ham ekran görüntüsü (Raw Screenshot) doğrudan Gemini 2.0 Flash modeline gönderilmektedir. Gemini, güçlü görme yeteneği (VLM) sayesinde görseldeki butonları ve alanları yorumlamaktadır. Ancak OmniParser entegre edilirse, görseldeki öğeler numaralandırılmış kutucuklar (bounding boxes) olarak işaretlenir ve modele bu işlenmiş görüntü verilir.
*   **UI Ağacı (PyWinAuto):** Şu an prompt içine UI ağacı (XML benzeri yapı) **eklenmemektedir**. Ajan görsel algıya (Vision) dayalı çalışmaktadır. Ancak `pywinauto`'nun `print_control_identifiers()` fonksiyonu kullanılarak ekranın metin tabanlı hiyerarşisi çıkarılıp prompta metin olarak eklenmesi mümkündür ve bu hibrit bir yaklaşım (Görsel + Yapısal) sağlar.

---

## 3. Görevleri Yaparken Nasıl Bir Çıktı Oluşuyor ve Bu Çıktıyı PyAutoGUI Nasıl Kullanıyor?

**Cevap:**

Ajanın düşünme (Think) aşamasından sonra ürettiği çıktı, katı bir **JSON** formatındadır.

**Örnek Çıktı:**
```json
{
  "thought": "WhatsApp uygulamasını başlatmak için Windows tuşuna basıp arama yapmam gerekiyor.",
  "action": {
    "tool_name": "execute_python",
    "parameters": {
      "code": "import pyautogui\nimport time\npyautogui.press('win')\ntime.sleep(1)\npyautogui.write('WhatsApp')\ntime.sleep(1)\npyautogui.press('enter')"
    }
  }
}
```

**İşleme Süreci:**
1.  `Agent Core` modülü bu JSON yanıtını ayrıştırır (parse eder).
2.  `tool_name`'in `execute_python` olduğunu tespit eder.
3.  `parameters` içindeki `code` string'ini (Python kodunu) alır.
4.  Bu kod string'ini `LocalMCPServer` sınıfındaki `execute_python` metoduna iletir.
5.  `execute_python` metodu, Python'un yerleşik `exec()` fonksiyonunu kullanarak bu string'i gerçek zamanlı olarak çalıştırır. Böylece `pyautogui` komutları işletim sistemine gönderilir.

---

## 4. RAG Yapısının Sonucu Prompta Ekleniyor mu? Ekleniyorsa Başarı Oranını Artırıyor mu?

**Cevap:**

*   **Ekleniyor mu:** Evet, ekleniyor. `MemoryManager` sınıfı, kullanıcının girdiği görevi (Query) alır, embedding'e (sayısal vektör) dönüştürür ve Pinecone veritabanında en yakın vektörleri arar.
*   **Başarıya Etkisi:** Kesinlikle artırır. Eğer Pinecone'dan dönen sonuçların benzerlik skoru (similarity score) belirlenen eşik değerin (örn. 0.7) üzerindeyse, bu sonuçlar "Geçmiş Deneyimler" başlığı altında prompta eklenir.
    *   **Örnek:** Ajan daha önce "Chrome'u aç" görevini başarıyla yaptıysa ve bu deneyim hafızadaysa, yeni görevde "Chrome aç" dendiğinde ajan sıfırdan düşünmek yerine hafızadaki başarılı kod bloğunu kopyalayıp kullanma eğiliminde olur. Bu da başarı oranını ve hızı ciddi ölçüde artırır.

---

## 5. PyAutoGUI'ye Çalıştırılabilir Kod Nasıl Veriliyor ve Nasıl Çalıştırılıyor?

**Cevap:**

Süreç "Metin Tabanlı Kod Üretimi" ve "Dinamik Kod Çalıştırma" prensibine dayanır:

1.  **Üretim:** LLM (Gemini), çözümün Python kodu olarak nasıl olması gerektiğini bilir ve bunu bir metin (string) olarak JSON içinde döndürür.
2.  **Transfer:** Bu metin, `Agent` katmanından `MCP Server` katmanına parametre olarak geçer.
3.  **Çalıştırma:** `MCP Server` içinde, güvenliği artırmak amacıyla kısıtlı bir `globals` sözlüğü (içinde sadece `pyautogui`, `pywinauto`, `time` gibi izin verilen kütüphaneler tanımlıdır) oluşturulur.
4.  **İnfaz:** `exec(code_string, safe_globals)` komutu çağrılır. Bu komut, string halindeki metni o an derler ve çalıştırır. Böylece ajan, kendi yazdığı kodu kendi üzerinde çalıştırmış olur.

---

## 6. RAG Yapısını Nasıl Geliştirebiliriz? (Örn: Teams Uygulaması İçin Veriseti)

**Cevap:**

RAG yapısını geliştirmek, ajanın "bilgi dağarcığını" genişletmek demektir. Teams gibi spesifik bir uygulama için şunlar yapılabilir:

1.  **Manuel "Few-Shot" Eğitimi:** Ajana Teams ile ilgili küçük görevler verip (Örn: "Teams'i aç", "Sohbet sekmesine tıkla") bu işlemler başarılı oldukça veritabanının doğal yollarla dolmasını sağlamak.
2.  **Sentetik Veri Girişi (Seeding):** Pinecone veritabanına manuel olarak `upsert` işlemi yaparak, başarılı senaryoları (Adım adım talimatlar ve kodlar) yüklemek. Örneğin: "Teams Arama Yapma" başlığıyla, arama çubuğuna nasıl gidileceğinin Python kodunu vektör olarak kaydetmek.
3.  **Dokümantasyon Embedding'i:** Microsoft Teams'in kullanım kılavuzlarını veya klavye kısayol listelerini metin parçalarına (chunks) bölüp embedding haline getirerek veritabanına eklemek. Ajan "Teams'de arama nasıl yapılır?" diye düşündüğünde bu dokümanı hatırlayacaktır.
4.  **Namespace Kullanımı:** Pinecone içinde `teams_data`, `chrome_data` gibi farklı isim alanları (namespaces) oluşturarak veriyi kategorize etmek ve aramayı daha hedefe yönelik yapmak.

---

## 7. Ekranı Anlamak İçin VLM Modeli Kullanmak Olur mu? Başarıyı Artırır mı?

**Cevap:**

Evet, şu anki projemizde zaten bir VLM (Vision Language Model) olan **Gemini 2.0 Flash** kullanılmaktadır.

*   **Neden Gerekli:** Geleneksel LLM'ler (sadece metin) ekranı göremez, sadece onlara tarif edilen (örn. UI ağacı) veriyi anlar. Ancak modern arayüzler (web sayfaları, özel uygulamalar) her zaman temiz bir UI ağacı sunmaz.
*   **Başarıya Etkisi:** VLM kullanmak başarıyı dramatik şekilde artırır. Model, insan gibi "Görüyorum, sağ üstte kırmızı bir çarpı butonu var" diyebilir. Koordinat hesaplaması, ikonun şekli veya rengi üzerinden çıkarım yapması VLM sayesinde mümkündür.

---

## 8. Görevleri Nasıl Daha İyi Planlayabiliriz?

**Cevap:**

Karmaşık görevlerde ajanın "kaybolmaması" için planlama yeteneği şu yöntemlerle geliştirilebilir:

1.  **Planner-Worker Mimarisi:** Tek bir ajan yerine iki ajan kullanmak.
    *   **Planner Ajan:** Görevi alır ve sadece adımları listeler (Kod yazmaz). Örn: 1. WhatsApp aç, 2. Kişiyi bul, 3. Mesaj yaz.
    *   **Worker Ajan:** Planner'dan gelen her bir alt adımı sırayla kodlayıp uygular.
2.  **Chain-of-Thought (CoT) Prompting:** Sistem promptunda ajanı "Önce düşün, planını madde madde yaz, sonra ilk adımı at" şeklinde zorlamak.
3.  **Öz-Düzeltme (Self-Correction):** Ajan hata aldığında (Python hatası veya görsel analiz sonucu işlemin gerçekleşmemesi), hatayı analiz edip yeni bir plan yapmasını sağlayan bir geri bildirim döngüsü kurmak.

---

## 9. RAG Yapısına Başarılı Görevleri Ekliyor muyuz? Pinecone Yapılandırması Nasıl Olmalı?

**Cevap:**

*   **Ekleme:** Evet, mevcut kodda `task_complete` aracı çağrıldığında ve sonuç başarılıysa, `MemoryManager.upsert_experience` fonksiyonu çalışır ve deneyim kaydedilir.
*   **Retrieve Kriteri:** Yeni gelen görevin metni (Query) ile veritabanındaki "Goal" (Hedef) metinlerinin kosinüs benzerliğine (Cosine Similarity) göre çekilir.
*   **Yapılandırma:** Pinecone yapısal olarak değil ama meta-veri (metadata) ve Namespace ile organize edilebilir:
    *   `namespace="successful_tasks"`: Sadece çalışan, doğrulanmış kodlar.
    *   `namespace="documentation"`: Kullanım kılavuzları.
    *   **Metadata:** Her kayda `{ "app": "WhatsApp", "type": "messaging", "status": "success" }` gibi etiketler eklenerek filtreleme yapılabilir.

---

## 10. Sistemin Genel Çalışma Prensibi (Workflow Örneği)

**Cevap:**

1.  **Başlatma:** Kullanıcı `python main.py` komutunu verir ve görevi girer: "Chrome'u aç".
2.  **Algı (Perception):** Ajan ekranın görüntüsünü çeker.
3.  **Hafıza (Memory):** "Chrome aç" ile ilgili eski kayıtları Pinecone'da arar.
4.  **Düşünme (Reasoning):** Gemini; ekran görüntüsünü, kullanıcı hedefini ve hafızadan gelen veriyi birleştirir. "Başlat menüsünü açıp Chrome yazmalıyım" diye düşünür.
5.  **Eylem (Action):** Gemini, `execute_python` aracı için gerekli Python kodunu üretir (`pyautogui.press('win')...`).
6.  **Yürütme (Execution):** MCP Sunucusu bu kodu çalıştırır. Ekranda Windows menüsü açılır ve Chrome yazılır.
7.  **Döngü:** Ajan tekrar ekrana bakar. Chrome'un açıldığını görür.
8.  **Tamamlama:** `task_complete` aracını çağırır ve "Chrome açıldı" der. Bu bilgi Pinecone'a kaydedilir.

---

## 11. Bu Yapıyı Yerel (Local) Bir Model ile Yapabilir miyiz? (LMStudio vb.)

**Cevap:**

Evet, mümkündür. Proje modüler olduğu için LLM sağlayıcısı değiştirilebilir.

*   **LLM:** LMStudio veya Ollama gibi araçlar genellikle OpenAI uyumlu bir API sunar. `config.py` ve `agent/core.py` dosyasında `google.generativeai` yerine `openai` kütüphanesi kullanılarak `base_url="http://localhost:1234/v1"` şeklinde yerel modele yönlendirme yapılabilir.
*   **VLM:** Eğer yerel modeliniz (Örn: LLaVA, BakLLaVA) görsel destekliyse aynı mantıkla çalışır. Desteklemiyorsa, ekran görüntüsünü metne döken (Image-to-Text) ayrı bir yerel model kullanmak gerekebilir.

---

## 12. Local VLM Modelimizi Fine-Tune Edersek Başarı Artar mı? Nasıl Yapılır?

**Cevap:**

*   **Etki:** Evet, genel amaçlı bir model yerine, özellikle Windows arayüzleri ve GUI otomasyonu üzerine eğitilmiş (Fine-tuned) bir model çok daha yüksek başarı sağlar. Model butonların ne olduğunu ve `pyautogui` ile onlara nasıl ulaşacağını daha iyi anlar.
*   **Nasıl Yapılır:**
    1.  **Veri Toplama:** Binlerce ekran görüntüsü ve bunlara karşılık gelen "Doğru Eylem" (Action/Code) çiftlerinden oluşan bir veri seti hazırlanır.
    2.  **Eğitim:** Bu veri seti ile QLoRA veya LoRA (Low-Rank Adaptation) teknikleri kullanılarak model eğitilir. Bu işlem için güçlü bir GPU gereklidir, ancak sıfırdan model eğitmekten çok daha hafiftir.
    3.  **Entegrasyon:** Eğitilen adaptör (adapter) modele yüklenir ve ajan bu modeli kullanır.

---

## 13. Anlık Görüntüyü Anlamada OmniParser veya Yerel Modeli Nasıl Geliştirebiliriz?

**Cevap:**

*   **Set-of-Mark (SoM) Prompting:** OmniParser gibi araçlar, ekran görüntüsündeki her öğeye bir numara veya etiket (mark) yapıştırır. Modele ham resim yerine bu etiketli resim verilir. Model "Koordinat (10, 20)" demek yerine "3 numaralı kutu" der. Bu, halüsinasyon oranını ciddi şekilde düşürür.
*   **Geliştirme:** Yerel VLM modeliniz için, sadece GUI öğelerini (butonlar, textboxlar) tespit etmeye yönelik bir nesne algılama (Object Detection) modeli (Örn: YOLO) ile hibrit bir yapı kurabilirsiniz. YOLO öğeleri bulur, koordinatları çıkarır; VLM ise hangi öğeye tıklanacağına karar verir.

---

## 14. OmniParser / VLM'in Görevleri Nelerdir? Prompta Nasıl Giriyor?

**Cevap:**

*   **OmniParser (Tespit):** "Ekranda 5 tane buton, 2 tane metin kutusu var. Koordinatları şunlar." (Yapısal Veri)
*   **VLM (Karar):** "Kullanıcı 'Gönder' dediğine göre, üzerinde ok işareti olan, sağ alttaki butona tıklamalıyım." (Anlamsal Veri)
*   **Prompta Giriş:** İdeal senaryoda OmniParser'ın işlediği **etiketli resim** (üzerinde numaralar olan screenshot) modele görsel olarak verilir. Ayrıca metin olarak "ID 1: Başlat Butonu, ID 2: Arama Kutusu" şeklinde bir liste de prompta eklenebilir.

---

## 15. LLM Modeli Görevi Nasıl Planlıyor ve Bunu Nasıl Geliştirebiliriz?

**Cevap:**

Mevcut yapıda planlama, prompt içindeki "Adım adım düşün" (Chain of Thought) talimatıyla yapılıyor.

**Geliştirme Yolları:**
*   **Ağaç Araması (Tree of Thoughts):** Modele tek bir plan yerine 3 farklı plan ürettirip, kendi kendine en mantıklısını seçtirmek.
*   **Hiyerarşik Planlama:** Görevi önce ana başlıklara bölmek (Örn: 1. Uygulamayı aç, 2. İşlemi yap, 3. Kapat), sonra her başlığı ayrı ayrı icra etmek.

---

## 16. Prompt Yapısından Çıkan Sonuç Nasıl Bir Yapıya Sahip ve PyAutoGUI Nasıl İşliyor?

**Cevap:**

Prompt sonucu bir **JSON Nesnesidir**.

```json
{
  "thought": "Furkan ismini aratmak için CTRL+F kısayolunu kullanmalıyım.",
  "action": {
    "tool_name": "execute_python",
    "parameters": {
      "code": "pyautogui.hotkey('ctrl', 'f')\ntime.sleep(0.5)\npyautogui.write('Furkan')"
    }
  }
}
```

**İşleme:**
1.  `server.py` bu JSON'u alır.
2.  `code` parametresindeki metni okur: `"pyautogui.hotkey('ctrl', 'f')..."`
3.  `exec()` fonksiyonu ile bu metni bilgisayarın işlemcisine gönderir.
4.  Bilgisayar sanki klavyede CTRL ve F tuşlarına basılmış gibi tepki verir.

---

## 17. Proje Genel Akışının Bir Örnekle Açıklaması

**Örnek Senaryo:** "Spotify'ı aç ve bir şarkı çal."

1.  **BAŞLANGIÇ:** Kullanıcı komutu verir.
2.  **DÖNGÜ 1 (Uygulama Açma):**
    *   **Gözlem:** Ajan masaüstünü görür.
    *   **Hafıza:** "Daha önce Spotify açmıştım, Win tuşunu kullanmıştım" bilgisini hatırlar.
    *   **Eylem:** `win` tuşuna basar, `Spotify` yazar, `enter`'a basar.
    *   **Sonuç:** Spotify açılır.
3.  **DÖNGÜ 2 (Şarkı Arama):**
    *   **Gözlem:** Spotify ana ekranını görür. Arama ikonunu (Büyüteç) fark eder.
    *   **Düşünce:** "Şarkı çalmak için önce arama yapmalıyım."
    *   **Eylem:** `ctrl + l` (Spotify arama kısayolu) yapar veya arama butonuna tıklama kodu üretir. Şarkı ismini yazar.
4.  **DÖNGÜ 3 (Çalma):**
    *   **Gözlem:** Şarkı listesi gelir. En üstteki şarkıyı görür.
    *   **Eylem:** İlk sonuca tıklamak için `enter`'a basar veya fareyi oraya götürüp tıklar.
5.  **BİTİŞ:** Şarkı çalmaya başlar. Ajan sesi duyamaz ama görsel olarak "Pause" butonunun belirdiğini (yani çaldığını) anlar ve görevi başarılı sayarak bitirir.

