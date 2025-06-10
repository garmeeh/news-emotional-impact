# Emotional Impact of the News

![News Sentiment Analysis](news.gif)

The code in this project is a result of an experiment that I kicked off in December 2024. The idea was to process news articles from various sources for the 3rd of 2025 (January 2025 to April 2025) and answer my questions is all news negative? To do this I first thought about using sentiment analysis but the results didn't quite match what I thought the article could make someone feel. So along side sentiment, I asked the LLM what **emotional impact** could this article have on the reader. I provided a list of options so that it was easier to compare articles over time.

Within this project we check the following with an LLM for each news article:

- emotional impact: Assign primary emotional impact tag and optionally two secondary ones. [view prompt](app/prompts/emotional-impact-tag-v1.txt)
- sentiment: Analyse the given news article headline and assign one of the following sentiment labels: Very Negative, Negative, Neutral, Positive, Very Positive [view prompt](app/prompts/headline-sentiment-v1.txt)
- clickbait score: Give a rating from 1 to 5 on level of clickbait for the title of the article. 5 being pure click bait. [view prompt](app/prompts/clickbait-score-v1.txt)
- category: Determine a primary category (the single best match) and up to two optional secondary categories from provided list. [view prompt](app/prompts/category-tag-v1.txt)

Set Up Env

```
cp .env.example .env
```

Install deps

```
poetry install --no-root
```

**ensure database is set up first**

Scripts:

Run feed scrape to add news articles to DB:

```bash
poetry run python -m app.services.feed_parser
```

I was running this hourly via a cron job.

To then run AI sentiment analysis: (requires news articles to be in the database)

```bash
poetry run python -m app.services.run_sentiment_analysis
```

There is a rate limited option in [run_sentiment_analysis.py](app/services/run_sentiment_analysis.py) if using a model that has low rate limits.

## Exporting Data

To prepare the data for Kaggle I have created a few helper scripts. You can use these to export your data into CSV files.

The following scripts should be run in order:

1.  **Export from Supabase**

    This script exports data from your Supabase database into CSV files. It fetches everything from the news articles table and the news sentiment table

    ```bash
    poetry run python -m scripts.export_kaggle_data_supabase_sdk
    ```

This could be enough for your use case at this point. The scripts below were then used to prepare my data for Kaggle.

2.  **Clean Data**

    This script cleans the exported CSV files. It removes entries with invalid dates (published before X date, see script) and ensures that articles have corresponding sentiment data. In my case I only have one sentiment per news article as I only ran it long term with a single LLM. You may need to adjust the script if this is not your case.

    ```bash
    poetry run python -m scripts.clean_data
    ```

3.  **Deduplicate Data**

    This script deduplicates the cleaned data based on article titles and sources to ensure unique entries. It removes them from both news articles and news sentiments.

    ```bash
    poetry run python -m scripts.deduplicate_data
    ```

4.  **Create Random Samples**

    This script creates a random sample of 100 rows from the final datasets, which can be useful for quick analysis or testing.

    ```bash
    poetry run python -m scripts.create_random_samples
    ```

## Database

I used **Supabase** for the project, you can set up by doing the following:

1. Ensure you have installed the [CLI](https://supabase.com/docs/guides/local-development/cli/getting-started?queryGroups=platform&platform=macos#installing-the-supabase-cli) or [update it](https://supabase.com/docs/guides/local-development/cli/getting-started?queryGroups=platform&platform=macos#updating-the-supabase-cli)

2. Run `supabase start`

3. Run `supabase db reset` (only required first time you run this project)

## Other Useful Info

### News Sources

You can find all the sources in [app/feed_sources.py](app/feed_sources.py). To give you an idea of how many articles this would result in, this table is result of just over 3 months of hourly cron checks:

| source            | total_articles |
| ----------------- | -------------- |
| Irish Examiner    | 2,091          |
| Irish Mirror      | 10,204         |
| RTE News          | 5,412          |
| Gript             | 1,269          |
| Irish Independent | 20,987         |
| BBC News          | 8,682          |
| Breaking News     | 7,313          |
| The Journal       | 4,968          |
| RTE               | 876            |
| Evoke             | 3,212          |
| The Irish Sun     | 38,925         |

Most sources have the required fields, but you can easily modify the code to map fields to the required ones. In hindsight I would've given every feed a unique source and merge with SQL later on. eg: The Irish Sun has many RSS feeds

### Prompting

You can find all the prompts in [app/prompts](app/prompts)

You can define prompt configs in [app/config/prompt_versions](app/config/prompt_versions), I have left in one for OpenAI, Gemini and Anthropic as examples. The prompt config allows you to use different prompts for each part of the analysis.

You set the version you want to use in: [app/config/prompt_config.py](app/config/prompt_config.py), currently set to `1` which is Gemini.

The original dataset used:

```
"model": "gemini-2.0-flash-001",
"temperature": 1
```

I tested a lot of models and found this to be the closest to what I and some colleagues judged to be correct. So somewhat biased.

The config used is stored in the database which allows you to run multiple different runs. You will just need to tweak the logic for retrieving articles as it defaults to just getting articles with no sentiment at present.

You can add other LLM providers in [app/llm/llm.py](app/llm/llm.py)

Example config from live database:

```json
{
  "clickbait": {
    "path": "prompts/clickbait-score-v1.txt",
    "model": "gemini-2.0-flash-001",
    "version": 9,
    "temperature": 1.0
  },
  "sentiment": {
    "path": "prompts/headline-sentiment-v1.txt",
    "model": "gemini-2.0-flash-001",
    "version": 9,
    "temperature": 1.0
  },
  "categories": {
    "path": "prompts/category-tag-v1.txt",
    "model": "gemini-2.0-flash-001",
    "version": 9,
    "temperature": 1.0
  },
  "emotional_impact": {
    "path": "prompts/emotional-impact-tag-v1.txt",
    "model": "gemini-2.0-flash-001",
    "version": 9,
    "temperature": 1.0
  }
}
```
