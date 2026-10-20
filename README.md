# FiberLab Mongolia

Монголын шилэн кабелийн сүлжээний загварчлал, bridge илрүүлэлт, нэг кабелийн тасралтын симуляци.

## 1. Шууд ажиллуулах

Python 3.9+, Node.js 20+ шаардана. Arch Linux дээр Python, Node.js, npm байх ёстой.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend/app.py
```

Энэ терминалыг нээлттэй байлгана. Өөр терминалд:

```bash
python -m http.server 8000 --directory dist --bind 127.0.0.1
```

Браузер: http://localhost:8000

`dist` дотор build хийсэн React интерфэйс бэлэн тул Node суулгахгүйгээр ашиглаж болно. Үндсэн тооцоолол браузерт ажиллана. Python API нь тусдаа reference engine; «Харьцуулалт → Локал Flask exact тооцоолол» товч API руу одоогийн өөрчилсөн графыг илгээнэ. HTTPS-ээр нийтлэгдсэн вебээс loopback API руу хандахыг браузер хааж болзошгүй тул exact туршилтыг localhost:8000 дээр хийнэ.

## 2. Source-оос build хийх

```bash
npm install
npm run build
npx tailwindcss -i src/tailwind.css -o dist/tailwind.css --minify
```

## 3. Туршилт

```bash
npm test
python -m pytest tests/test_backend.py -q
```

Шалгалтууд: MST n−1 ирмэгтэй; Full Mesh 231 ирмэгтэй; MST-ийн бүх ирмэг bridge; 2-Edge-ийн бүх ирмэгийг тус тус таслахад граф холбоотой; rerouting тасарсан холбоос ашиглахгүй; exact арга жижиг графын exhaustive enumeration-тэй таарна; API болон алдаатай input шалгалт.

## 4. Хэрэглэх дараалал

1. «Сүлжээний загвар»-т MST сонгож, кабель сонгоод тасална. Тусгаарлагдсан хотуудыг харна.
2. Кабелийг сэргээгээд 2-Edge сонгоно. Ижил үйлдлээр нөөц зам ажиллаж буйг харна.
3. Урсгалын эхлэл, төгсгөлийг сонгоход latency жинтэй shortest path ягаан өнгөөр харагдана.
4. «Зангилаа ба трасс»-т зангилаа/трасс нэмэх, засах, хасах, JSON import/export хийж болно. Шинэ зангилаанд хоёр өөр нөөц чиглэл шаардлагатай.
5. «Харьцуулалт»-д нэгж уртын CAPEX ба төхөөрөмжийн хоцролтыг өөрчилнө. API ажиллаж байвал exact тооцоог авна.
6. Тайлан экспортлох нь JSON үр дүн татна. localStorage нь тухайн браузерийн өгөгдлийг хадгална. Өөр компьютер руу шилжүүлэхдээ JSON экспортлоно.

## 5. API

- `GET /api/health`
- `GET /api/network/topologies` — default dataset + greedy.
- `POST /api/network/topologies` — `{nodes, edges, method: "greedy"|"exact", hop_ms: 0.1}`. Nodes/edges-ийг орхивол default dataset.
- `POST /api/network/simulate-cut` — `{topology: "mst"|"resilient"|"mesh", edge_id: "dar--ub", source: "ulg", target: "dorn", anchor: "ub", method: "greedy"}`. Өөрчилсөн графын nodes/edges-ийг мөн дамжуулж болно.

Алдаатай параметрт 400 JSON error буцаана. Input ≤100 node, payload ≤2 MiB. Flask loopback дээр, debug=False. Олон хэрэглэгчийн production API hosting энэ хувилбарт ороогүй.

## 6. Файлын бүтэц

- `src/app.jsx`: React интерфэйс + Leaflet картаар дүрслэх.
- `src/engine.mjs`: Kruskal, Tarjan, greedy augmentation, routing, RTT.
- `src/style.css`, `src/tailwind.css`: responsive дизайн, Tailwind.
- `backend/engine.py`: NetworkX reference engine + SciPy MILP.
- `backend/app.py`: Flask REST API.
- `data/network.json`: 22 зангилааны загварын өгөгдөл.
- `data/reference-results.json`: Python exact жишиг тооцоо.
- `DESIGN.md`: нарийвчилсан шаардлага, архитектур, үр дүн, хамгаалах тайлбар.
- `tests/`: graph engine ба API шалгалт.

## 7. Өгөгдөл ба хязгаарлалт

Солбицол ойролцоо, баталгаажсан GIS өгөгдөл биш. Зайг Haversine ×1.25 гэж авсан; бодит авто/төмөр замын урт биш. Candidate графыг дөрвөн ойрын хөрш + conceptual perimeter байдлаар үүсгэсэн; барих боломж, газарзүйн эрсдэлийг шалгаагүй. Газрын зураг дээрх шулуун холбоос нь кабелийн бодит route geometry биш.

RTT нь 0.005 ms/km one-way ба default 0.1 ms/link төхөөрөмжийн тогтмол хоцролтыг ашигласан estimate. Traffic volume, capacity, queueing, convergence time-ийг оруулаагүй. Нэг зангилааны эвдрэл эсвэл нэг газар дахь олон кабелийн хамтын гэмтлээс хамгаалах баталгаа байхгүй.

Газарзүйн зураг (Esri Topo / World Imagery) ба нэмэлт веб font интернет шаарддаг. CARTO tile сервер API key шаардаж эхэлсэн тул түүнийг ашиглахаа зогсоосон. Анхны дэлгэц нь интернетээс хамаарахгүй солбицолд суурилсан схем. React, Leaflet болон үндсэн engine локал bundle дотор байна.

## 8. v2 харагдах байдал

Network Observatory дизайн: нарийн навигацийн зурвас, зураг голлосон ажлын талбар, тасралтын самбар, хөдөлгөөнт урсгал. Dark/Light товч баруун дээд буланд; сонголт localStorage-д хадгалагдана. Газрын зургийг томруулах товчтой, Esc дарж буцаана. Reduced-motion системийн тохиргоог хүндэтгэнэ.

Chrome браузерт хоёр горим, горим хадгалах, томруулах/буцаах, кабель таслах/сэргээх болон харьцуулалтын хуудсыг шалгасан. Firefox/Edge болон гар утсан дээр төхөөрөмжийн бодит шалгалт хийгдээгүй.
