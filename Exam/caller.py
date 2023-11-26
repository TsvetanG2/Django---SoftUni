import os
import django
from django.db.models import Count, Avg, Subquery, F
from main_app.models import Author, Article, Review
from django.db import models

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orm_skeleton.settings")
django.setup()


def get_authors(search_name=None, search_email=None):
    if search_name is not None and search_email is not None:
        matching_authors = Author.objects.filter(
            full_name__icontains=search_name,
            email__icontains=search_email)
    elif search_name is not None:
        matching_authors = Author.objects.filter(full_name__icontains=search_name)
    elif search_email is not None:
        matching_authors = Author.objects.filter(email__icontains=search_email)
    else:
        return ""

    matching_authors = matching_authors.order_by('-full_name')

    result_string = ""
    for author in matching_authors:
        status = "Banned" if author.is_banned else "Not Banned"
        result_string += f"Author: {author.full_name}, email: {author.email}, status: {status}\n"

    return result_string.strip()


def get_top_publisher() -> str:
    top_publisher = Author.objects.get_authors_by_article_count().filter(article_count__gt=0).first()

    if top_publisher:
        return f"Top Author: {top_publisher.full_name} with {top_publisher.article_count} published articles."

    return ""


def get_top_reviewer() -> str:
    top_reviewer = Author.objects.annotate(num_of_reviews=Count('reviews')).filter(num_of_reviews__gt=0).order_by('-num_of_reviews', 'email').first()

    if top_reviewer:
        return f"Top Reviewer: {top_reviewer.full_name} with {top_reviewer.num_of_reviews} published reviews."

    return ""


def get_latest_article():
    latest_article_subquery = (
        Article.objects.filter(published=True)
        .order_by('-publish_date')
        .values('id')[:1]
    )

    latest_article = (
        Article.objects.filter(id=Subquery(latest_article_subquery))
        .prefetch_related('authors')
        .annotate(
            authors_names=F('authors__full_name'),
            num_reviews=Count('reviews__id'),
            avg_rating=Avg('reviews__rating'),
        )
        .values('title', 'authors_names', 'num_reviews', 'avg_rating')
        .first()
    )

    if not latest_article:
        return ""

    avg_rating_formatted = "{:.2f}".format(latest_article['avg_rating'] or 0.0)

    result_string = (
        f"The latest article is: {latest_article['title']}. "
        f"Authors: {latest_article['authors_names']}. "
        f"Reviewed: {latest_article['num_reviews']} times. "
        f"Average Rating: {avg_rating_formatted}."
    )

    return result_string


def get_top_rated_article() -> str:
    top_rated_article = Article.objects.annotate(avg_rating=Avg('reviews__rating')).filter(
        reviews__isnull=False).order_by('-avg_rating', 'title').first()

    if top_rated_article:
        num_reviews = top_rated_article.reviews.count()
        avg_rating = top_rated_article.avg_rating

        return f"The top-rated article is: {top_rated_article.title}, with an average rating of {avg_rating:.2f}, reviewed {num_reviews} times."

    return ""


def ban_author(email=None) -> str:
    if email is None:
        return "No authors banned."

    try:
        author = Author.objects.get(email=email)
    except Author.DoesNotExist:
        return "No authors banned."

    num_reviews = author.reviews.count()
    author.is_banned = True
    author.save()
    author.reviews.all().delete()

    return f"Author: {author.full_name} is banned! {num_reviews} reviews deleted."
