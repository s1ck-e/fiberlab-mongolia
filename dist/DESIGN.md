# Шилэн кабелийн сүлжээний загварчлал ба симуляцийн систем

## Төслийн зорилго

Улаанбаатар болон 21 аймгийн төвийг холбох магистраль сүлжээний нийт урт, нэг кабелийн тасралтын эрсдэл, нөөц замын үр нөлөөг харьцуулах сургалтын веб систем. 22 цэгийг хотын түвшинд тогтоосон: аймгийн нэрээр дурдсан Сэлэнгэ, Хэнтий нь Сүхбаатар, Чингис хот болно. Дархан, Эрдэнэт аймгийн төвөөр багтана.

## Нягталсан шаардлага

| ID | Шаардлага | Хүлээн авах шалгуур / хэрэгжилт |
|---|---|---|
| FR-1.1 | Чиглэлгүй, эерэг км жинтэй граф | Улаанбаатар +21 төв; JSON; endpoint ба weight validation |
| FR-1.2 | Node/edge нэмэх, хасах, засах | React CRUD; localStorage; JSON import/export |
| FR-2.1 | MST | Kruskal; холбоотой үед n−1 ирмэг; нийт урт |
| FR-2.2 | Bridge | JS Tarjan DFS; Python nx.bridges |
| FR-2.3 | 2-edge-connected augmentation | Greedy + pruning; optional fixed-MST exact MILP |
| FR-3.1 | Cut-edge test | Сонгосон ганц ирмэгийг хасах; components/is_connected |
| FR-3.2 | Нөлөөлөл | Улаанбаатартай холбогдоогүй хотууд; UB байхгүй бол эхний node-г anchor болгоно |
| FR-3.3 | Rerouting | Latency жинтэй shortest path; тасарсан ирмэгийг ашиглахгүй |
| FR-4.1 | Geographic rendering | Leaflet / Esri зураг, бие даасан схем; MST улаан, 2-Edge цэнхэр, Full Mesh ногоон |
| FR-4.2 | Харьцуулалт | Урт, CAPEX, bridge, estimated RTT, нэмэлт уртын хувь |
| NFR-1 | Үндсэн тооцоо <1s | 22-node dataset-д хэмжих зорилт; exact 5s solver limit тусдаа |
| NFR-2 | Browser compatibility | Standard React/JS; Chrome/Firefox/Edge-ийн бодит UI тест хийгдээгүй |
| NFR-3 | Өргөтгөл | Engine нь node тоонд hard-code хийгдээгүй; v1 import cap 100 node |

Бодит замын урт, route geometry, газарзүйн эрсдэлийн penalization optional бөгөөд v1-д ороогүй. Шинэ хот нэмэх нь алгоритмын код өөрчлөхгүй; гэхдээ боломжит графын холбоосуудыг хэрэглэгч нэмнэ.

## Архитектур

React + TailwindCSS интерфэйс нь Dataset → JS Graph Engine → map/statistics/cut simulation гэсэн урсгалтай. Браузерт ажиллах engine нь онлайн демог Python сервергүй ашиглах боломжтой болгоно. NetworkX дээрх тусдаа Python reference engine-ийг Flask REST API-гаар ажиллуулж, exact augmentation-тай харьцуулна. Hosted Sites нь статик bundle түгээнэ; Flask-ийг Sites дээр deploy хийгээгүй. Shared database, олон хэрэглэгчийн collaboration энэ хувилбарт байхгүй.

Браузерийн хадгалалт нь зөвхөн localStorage; экспортлосон dataset-ийг дараа нь import хийж туршилтыг дахин гаргаж болно.

## Алгоритмын үндэслэл

### MST

Kruskal: ирмэгүүдийг км-ээр эрэмбэлж, өөр өөр компонентуудыг нэгтгэх ирмэгийг авна. Холбоотой граф дээр n−1 ирмэг үүсгэнэ. Ийм модны бүх ирмэг bridge тул хамгийн хямд холболт нь дангаараа нэг кабелийн гэмтлийг тэсвэрлэхгүй.

### Bridge ба 2-edge connectivity

Tarjan DFS нь tin[u], low[u]-г хадгална. DFS модны (u,v) ирмэгт low[v] > tin[u] бол bridge. Хугацааны төвөгшил O(V+E). Холбоотой бөгөөд bridge-гүй чиглэлгүй граф дээр дурын нэг ирмэгийг хасахад граф холбоотой хэвээр байна. Энэ нь нэг ирмэгийн гэмтэлд хамаарна; articulation vertex болон shared risk group-д хамаарахгүй.

### Greedy augmentation

Одоогийн bridge-үүдийг хамгийн бага km/newly-covered-bridges харьцаагаар хамгаалах боломжит ирмэгийг нэмнэ. Ирмэг нэмэх нь түүний төгсгөлийн хооронд цикл үүсгэж олон bridge-ийг зэрэг хамгаалж болно. Bridge үлдэхгүй болтол давтаж, дараа нь өндөр өртөгтэй илүүдэл нэмэлт ирмэгүүдийг хасна. Exact optimum батлахгүй.

Боломжит трассын эх граф өөрөө bridge-тэй бол тухайн bridge-г ямар ч дэд граф хамгаалж чадахгүй. Иймд 2-edge топологи боломжгүй гэсэн алдаа харуулж, шинэ нөөц трасс оруулах шаардлагатай.

### Fixed-MST exact formulation

MST-ийн ирмэгийг eᵢ, нэмэх боломжтой холбоосыг aⱼ гэж авна. aⱼ нь MST-ийн төгсгөл хоорондын зам дээрх ирмэгүүдийг циклээр хамгаална. Aᵢⱼ =1 бол eᵢ энэ замд байна.

min Σ wⱼxⱼ, нөхцөл A x ≥1, xⱼ ∈ {0,1}.

SciPy MILP / HiGHS ашиглана. Solver status optimal байвал зөвхөн энэ тогтмол MST-ийн хамгийн бага augmentation гэж дүгнэнэ. Бүх боломжит spanning subgraph дундах глобал 2-edge optimum гэж дүгнэхгүй. Time limit 5 секунд; хугацаа хүрсэн үед feasible result-ийг optimal гэж нэрлэхгүй.

Албан баримт: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html
NetworkX weighted augmentation-ийн approximation тайлбар: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.connectivity.edge_augmentation.k_edge_augmentation.html

### RTT ба зардал

One-way link latency = km × 0.005 ms + dₕₒₚ. Default dₕₒₚ =0.1 ms/link. RTT =2 × shortest one-way path latency. Бүх хосын хамгийн их утгыг max RTT гэж авна. Граф салсан үед max RTT finite биш тул Python JSON-д null, UI-д ∞ гэж тэмдэглэнэ. Delay жин routing-д ашиглагдана.

CAPEX = Σ km × unit_cost_MNT. Default 10,000,000 ₮/km нь жишээ параметр бөгөөд үнийн санал биш. Cable/core count, civil works, equipment, permits, OPEX зэргийг бүрэн тооцоогүй.

Нэмэлт урт (%) =(L₂edge−Lₘₛₜ)/Lₘₛₜ ×100. 15–20% бол хүссэн зорилт; математик баталгаа биш.

## Туршилтын үр дүн

Ойролцоо 22 координат, Haversine ×1.25 уртын estimate, хийсвэр candidate graph дээр:

| Загвар | Нийт урт (км) | Bridge | Нэмэлт урт | Max RTT (ms) |
|---|---:|---:|---:|---:|
| MST | 4,935.4 | 21 | 0% | 36.800 |
| Greedy 2-Edge | 7,570.7 | 0 | 53.4% | 31.902 |
| Fixed-MST exact 2-Edge | 7,176.5 | 0 | 45.4% | 34.241 |
| Онолын Full Mesh | 190,534.0 | 0 | 3,760.6% | 22.747 |

Greedy 2-Edge дээр 28 холбоос байна. Бүх 28 холбоосыг тус тус таслахад граф холбоотой үлдсэн; хамгийн муу тасралтын max estimated RTT 36.326 ms. Exact загварын бүх холбоосыг нэг нэгээр таслах connectivity шалгалт мөн амжилттай. Full Mesh =231 ирмэг.

Exact урт greedy-ээс 394.2 км бага. Гэвч яг энэ шийдлийн max RTT greedy-ээс өндөр: уртын зорилт ба latency зорилт өөр болохыг харуулна. MILP-д 50 ms constraints ороогүй; RTT-г үр дүнд шалгана. Өгөгдөл өөрчлөгдвөл босго давж болно.

JS 6 тест, Python 3 тест амжилттай. Өгөгдсөн dataset дээр Python exact бүх топологи боловсруулах нэг хэмжилт ~11 ms байсан; энэ нь бүх төхөөрөмж, шинэ өгөгдөл, бүх API request-д <1s баталгаа биш. Хүйтэн старт болон орчны ялгаа нөлөөлнө. v2 шинэчлэлд Chrome дээр Dark/Light, сонголт хадгалах, томруулах/буцаах, кабель таслах/сэргээх, харьцуулалтын хуудсыг шалгасан. Firefox/Edge дээр шалгаагүй.

## Багшид хамгаалах товч тайлбар

“Би хотуудыг зангилаа, шилэн кабелийг км жинтэй ирмэг болгон загварчилсан. Эхлээд Kruskal-аар хамгийн бага нийт урттай MST байгуулсан. Гэвч модны бүх холбоос критик тул нэг кабель тасрахад хэсэг хот сална. Дараа нь критик холбоосуудыг циклд оруулах нөөц кабель нэмсэн. Tarjan-аар bridge тэг болсныг шалгаад, кабель бүрийг нэг нэгээр тасалж бүх хот холбоотой үлдсэнийг баталгаажуулсан. Greedy ба exact тооцооны ялгааг харьцуулсан. Миний зай нь бодит замын хэмжилт биш учраас үр дүнг сургалтын загвар гэж тайлагнасан.”

## Дараагийн шат

Баталгаажсан city coordinates, авто/төмөр замын route geometry/км dataset оруулах; candidate corridor feasibility шалгах; common-risk бүлэг, багтаамж, demand болон recovery time нэмэх; шаардлагатай бол latency-constrained global 2-edge optimization судлах.
