"""Application definition."""
from bocadillo import App, discover_providers, Templates, settings
from tortoise import Tortoise
from tortoise.query_utils import Q

from .models import BookSummary
from .pagination import Pagination

app = App()
templates = Templates(app)
discover_providers("librarian.providerconf")


@app.on("startup")
async def init_db():
    await Tortoise.init(
        db_url=str(settings.get("DATABASE_URL")), modules={"models": ["librarian.models"]}
    )
    await Tortoise.generate_schemas()


@app.on("shutdown")
async def db_cleanup():
    await Tortoise.close_connections()


@app.route("/")
async def index(req, res):
    res.html = await templates.render("index.html")


@app.route("/search")
async def search(req, res):
    search_query = req.query_params.get("q", "")
    page = int(req.query_params.get("page", 1))
    if search_query:
        words = search_query.strip().split(" ")
        q = Q(isbn__in=words)
        for word in words:
            q |= Q(title__icontains=word)
            q |= Q(publisher__icontains=word)
            q |= Q(author__icontains=word)
        summaries = BookSummary.filter(q).order_by("-isbn")
    else:
        summaries = BookSummary.all().order_by("-isbn")

    total = await summaries.count()
    paginator = Pagination(summaries, per_page=10, current_page=page)
    summaries = await paginator.paginate()

    res.html = await templates.render(
        "search.html",
        summaries=summaries,
        q=search_query,
        page=page,
        paginator=paginator,
        total=total,
    )


@app.route("/book/{isbn}")
async def book_detail(req, res, isbn):
    summary = await BookSummary.get(isbn=isbn)
    res.html = await templates.render("book.html", summary=summary)
