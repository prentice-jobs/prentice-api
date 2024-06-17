import http
from fastapi import (
    APIRouter,
    Depends,
    Body,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi.encoders import jsonable_encoder

from src.company.models import Companies
from src.company.schema import CompanyCreate, CompanyName, CompanyUpdate
from src.company.service import CompanyService
from src.core.schema import GenericAPIResponseModel
from src.company import service, schema
from src.review.services.upload_service import UploadService
from src.utils.db import get_db

VERSION = "v1"
ENDPOINT = "company"

company_router = APIRouter(prefix=f"/{VERSION}/{ENDPOINT}", tags=[ENDPOINT])

@company_router.get(
    "/all",
    response_description="Fetch all the companies",
    status_code=http.HTTPStatus.OK,
)
def fetch_all_companies(db: Session = Depends(get_db)):
    service = CompanyService()
    companies = service.get_all_companies(db)
    return companies

@company_router.get("/test",
                    status_code=http.HTTPStatus.OK,
                    )
def test(db: Session = Depends(get_db)):
    service = UploadService()

    input_strings = [
        "Jadi, gue magang di perusahaan IT ini, dan beneran, gue kaget banget sama fasilitasnya.",
        "Kaya hotel bintang lima, deh!",
        "Tempat tidur empuk, AC dingin, dan makanan enak.",
        "Eh, tapi jujur aja, gue agak kecewa sama timnya.",
        "Kayaknya mereka kurang kompak gitu.",
        "Kadang-kadang ada yang nggak koordinasi, jadi proyek jadi berantakan.",
        "Gue sampe mikir, ‘Ini tim kerja apa tim basket?’",
        "Gue sih biasa aja.",
        "Magang di sini lumayan lah.",
        "Kerjaannya nggak terlalu berat, tapi juga nggak terlalu ringan.",
        "Gue suka sama suasana kantornya, sih.",
        "Ada tanaman-tanaman gitu, bikin adem.",
        "Tapi ya gitu, nggak ada yang istimewa banget.",
        "Saya merasa beruntung bisa magang di PT Carakan Sadhana Dirgantara.",
        "Pengalaman ini membuka wawasan saya tentang dunia kerja di industri IT.",
        "Meskipun ada tantangan, seperti kesulitan mengikuti pelajaran di sekolah, saya tetap berusaha semaksimal mungkin.",
        "Saya mengikuti magang di PT Carakan Sadhana Dirgantara, sebuah perusahaan IT yang bergerak di bidang pengembangan perangkat lunak.",
        "Selama delapan bulan berada di perusahaan ini, saya memiliki peran ganda sebagai programmer game dan juga ketua tim.",
        "Meskipun jadwal magang penuh, saya merasa bersyukur karena kesempatan ini memberikan ilmu berharga bagi saya.",
        "Di industri, saya disuguhi fasilitas yang sangat mewah dan makanan yang sudah tersedia.",
        "Manajemen waktu juga menjadi kunci penting di dunia industri.",
        "Untuk mencapai target secara optimal dan efisien, saya harus disiplin dalam membagi waktu antara istirahat dan pekerjaan.",
        "Saya percaya bahwa melengkapi diri dengan pengetahuan baru di luar tugas magang saya dapat memberikan manfaat jangka panjang dalam perjalanan karier saya.",
        "Dalam meniti karir di era digital, Generasi Z menemui peluang besar melalui pengalaman magang.",
        "Magang bukan hanya sekadar tahap awal dalam memasuki dunia kerja, tetapi juga merupakan fondasi penting dalam membentuk karier yang sukses dan memenuhi tuntutan perusahaan di era digital ini.",
        "Saya mengikuti magang di PT Carakan Sadhana Dirgantara, sebuah perusahaan IT yang bergerak di bidang pengembangan perangkat lunak.",
        "Dalam magang ini, saya terlibat dalam pengembangan game menggunakan teknologi Unreal Engine 5 yang sangat menarik.",
        "Bidang ini berkaitan erat dengan tren terkini tentang metaverse yang sedang booming saat ini.",
        "Gue suka banget sama mentor gue di sini.",
        "Mereka nggak cuma ngajarin soal coding, tapi juga ngasih insight tentang industri IT secara keseluruhan.",
        "Jadi, gue bener-bener dapet ilmu yang nggak bisa gue dapetin di kampus.",
        "Tapi, ya, ada juga sih yang bikin gue kesel.",
        "Beberapa kali gue ngerasa nggak dihargai.",
        "Gue ngelakuin kerjaan yang lumayan berat, tapi nggak pernah diapresiasi.",
        "Jadi, ya, agak ngerusak mood gue.",
        "Tempatnya strategis banget, deh.",
        "Deket kampus, deket tempat makan, deket minimarket.",
        "Jadi, kalo lagi laper, tinggal jalan bentar aja udah dapet makanan enak.",
        "Saya benar-benar terkesan dengan kecanggihan teknologi yang digunakan di perusahaan ini selama magang saya.",
        "Para senior sangat membantu, selalu siap sedia untuk membimbing kami, para magang.",
        "Ruang kerja yang nyaman dan teknologi terkini membuat pengalaman magang ini sangat berharga.",
        "Kesempatan untuk bekerja pada proyek besar adalah pengalaman yang tak ternilai bagi saya.",
        "Kultur perusahaan yang inklusif membuat saya cepat beradaptasi dan belajar banyak hal baru.",
        "Pekerjaan saya sebagai magang di departemen pemasaran membawa banyak tantangan yang menarik dan pengalaman belajar.",
        "Selama magang, saya terlibat dalam beberapa proyek yang memperkenalkan saya pada dunia kerja nyata di industri IT.",
        "Kebebasan untuk bereksplorasi dan mengekspresikan ide-ide kreatif sangat dihargai di tempat magang saya.",
        "Saya mendapatkan banyak kesempatan untuk menghadiri pertemuan dengan klien, yang sangat membangun kepercayaan diri saya.",
        "Mendapatkan feedback langsung dari klien adalah bagian dari proses belajar saya selama magang.",
        "Fasilitas seperti gym dan kafe di kantor membuat lingkungan kerja sangat menyenangkan.",
        "Saya merasa sangat diterima di tim saya, dan ini membuat seluruh pengalaman magang sangat menyenangkan.",
        "Menjadi bagian dari tim yang bekerja pada pengembangan aplikasi mobile adalah mimpi yang menjadi kenyataan bagi saya.",
        "Saya belajar banyak tentang pengembangan perangkat lunak dan manajemen proyek selama magang.",
        "Mentor saya sangat berpengalaman dan selalu bersedia menjawab pertanyaan apapun yang kami miliki.",
        "Tantangan terbesar saya adalah mengikuti jadwal yang ketat dan memenuhi deadline yang seringkali sangat mendesak.",
        "Saya terkejut dengan seberapa cepat saya bisa belajar dan beradaptasi dengan lingkungan perusahaan yang sangat dinamis.",
        "Tim IT sangat solid dan bekerja sebagai satu kesatuan, yang membuat proyek-proyek berjalan lancar.",
        "Saya mengapresiasi kesempatan untuk bekerja secara langsung dengan teknologi canggih yang tidak diajarkan di universitas.",
        "Akhir magang saya ditandai dengan presentasi proyek kepada manajemen, yang merupakan pengalaman yang sangat membangun."
    ]

    test = service.keyword_extractor(input_strings, "PT Carakan Sadhana Dirgantara")

    return test

@company_router.get(
    "/search-name",
    response_description="Search companies by name",
    status_code=http.HTTPStatus.OK,
)
def search_company_by_name(name: str = Query(..., description="Name of the company to search for"), db: Session = Depends(get_db)):
    service = CompanyService()
    companies = service.search_companies_by_name(db, name=name)
    return companies

@company_router.get(
    "/search-tags",
    response_description="Search companies by name or tags",
    status_code=http.HTTPStatus.OK,
)
def search_company(
    name: str = Query(None, description="Name of the company to search for"),
    tags: str = Query(None, description="Comma-separated tags to filter companies"),
    db: Session = Depends(get_db)
):
    service = CompanyService()
    companies = service.search_companies_by_tags(db, name=name, tags=tags)
    return companies

@company_router.get(
    "/{company_id}",
    response_description="Fetch a specific company",
    status_code=http.HTTPStatus.OK,
)
def fetch_company_by_id(company_id: UUID, db: Session = Depends(get_db)):
    service = CompanyService()
    db_company = service.get_company_by_id(db=db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@company_router.post("/", status_code=http.HTTPStatus.CREATED)
def create_company(db: Session = Depends(get_db), payload: CompanyCreate = Body()):
    service = CompanyService()

    req_company = CompanyCreate(
        id=payload.id,
        created_at=payload.created_at,
        updated_at=payload.updated_at,
        is_deleted=payload.is_deleted,
        display_name=payload.display_name,
        logo_url=payload.logo_url,
        star_rating=payload.star_rating,
        company_sentiment=payload.company_sentiment,
        description=payload.description,
        tags=payload.tags,
        review_count=payload.review_count,
        company_review=payload.company_review,
    )

    payload_json = jsonable_encoder(req_company)
    company = service.create_company(db=db, payload=payload_json)

    return company


@company_router.patch(
    "/{company_id}",
    status_code=http.HTTPStatus.OK,
)
def update_company(
    company_id: str, company: CompanyUpdate, db: Session = Depends(get_db)
):
    service = CompanyService()

    db_company = service.update_company(db, company_id=company_id, company=company)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@company_router.delete(
    "/{company_id}",
    status_code=http.HTTPStatus.OK,
)
def delete_company_by_id(company_id: UUID, db: Session = Depends(get_db)):
    service = CompanyService()
    db_company = service.delete_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company
