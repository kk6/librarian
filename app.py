from bocadillo import App, Templates
from tortoise import Tortoise
from tortoise.query_utils import Q

from models import BookSummary

app = App()
templates = Templates(app)


@app.on("startup")
async def init_db():
    await Tortoise.init(db_url="sqlite://db.sqlite3", modules={"models": ["models"]})
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
        summaries = await BookSummary.filter(
            Q(isbn__in=words)
            | Q(title__in=words)
            | Q(publisher__in=words)
            | Q(author__in=words)
        ).order_by("title")

    else:
        summaries = await BookSummary.all().order_by("title")
    res.html = await templates.render(
        "search.html", summaries=summaries, q=search_query, page=page
    )


@app.route("/book/{isbn}")
async def book_detail(req, res, isbn):
    summary = await BookSummary.get(isbn=isbn)
    res.html = await templates.render("book.html", summary=summary)


@app.route("/home")
async def home(req, res):
    await BookSummary.create(
        isbn="aaa1111",
        title="ほげ",
        volume="1",
        series="s1",
        author="hogesan",
        publisher="ほげ 出版",
        pubdate="20190401",
        cover="hoge.jpg",
    )
    # Fetch all posts along with their categories
    summaries = await BookSummary.all()
    # Render a template that lists all posts
    res.html = await templates.render("home.html", summaries=summaries)


if __name__ == "__main__":
    app.run(debug=True)
