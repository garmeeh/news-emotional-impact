set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.get_joined_sentiments_paginated(page_limit integer, page_offset integer)
 RETURNS TABLE(sentiment_id bigint, sentiment_created_at timestamp with time zone, news_article_id bigint, sentiment_label text, sentiment_confidence integer, clickbait_level smallint, version_info jsonb, article_title text, article_url text, article_description text, article_original_category text, article_media_url text, article_publish_date timestamp with time zone, article_source text, primary_category_tag_name text, secondary_category_tag_names text[], primary_emotional_impact_tag_name text, secondary_emotional_impact_tag_names text[])
 LANGUAGE sql
AS $function$
SELECT
  nas.id AS sentiment_id,
  nas.created_at AS sentiment_created_at,
  nas.news_article_id,
  nas.sentiment_label,
  nas.sentiment_confidence,
  nas.clickbait_level,
  nas.version_info,
  na.title AS article_title,
  na.url AS article_url,
  na.description AS article_description,
  na.category AS article_original_category,
  na.media_url AS article_media_url,
  na.publish_date AS article_publish_date,
  na.source AS article_source,
  primary_cat.tag_name AS primary_category_tag_name,
  secondary_cats.tag_names AS secondary_category_tag_names,
  primary_emo.tag_name AS primary_emotional_impact_tag_name,
  secondary_emos.tag_names AS secondary_emotional_impact_tag_names
FROM
  (SELECT * FROM public.news_article_sentiments ORDER BY id LIMIT page_limit OFFSET page_offset) nas
  LEFT JOIN public.news_articles na ON nas.news_article_id = na.id
  LEFT JOIN LATERAL (
    SELECT ct.tag_name
    FROM public.news_article_tags nat
    JOIN public.category_tags ct ON nat.category_tag_id = ct.id
    WHERE nat.news_article_sentiment_id = nas.id AND nat.is_primary = TRUE
    LIMIT 1
  ) primary_cat ON TRUE
  LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(DISTINCT ct.tag_name ORDER BY ct.tag_name) AS tag_names
    FROM public.news_article_tags nat
    JOIN public.category_tags ct ON nat.category_tag_id = ct.id
    WHERE nat.news_article_sentiment_id = nas.id AND (nat.is_primary = FALSE OR nat.is_primary IS NULL)
  ) secondary_cats ON TRUE
  LEFT JOIN LATERAL (
    SELECT eit.tag_name
    FROM public.news_article_emotional_impact naei
    JOIN public.emotional_impact_tags eit ON naei.emotional_impact_tag_id = eit.id
    WHERE naei.news_article_sentiment_id = nas.id AND naei.is_primary = TRUE
    LIMIT 1
  ) primary_emo ON TRUE
  LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(DISTINCT eit.tag_name ORDER BY eit.tag_name) AS tag_names
    FROM public.news_article_emotional_impact naei
    JOIN public.emotional_impact_tags eit ON naei.emotional_impact_tag_id = eit.id
    WHERE naei.news_article_sentiment_id = nas.id AND (naei.is_primary = FALSE OR naei.is_primary IS NULL)
  ) secondary_emos ON TRUE
ORDER BY nas.id; -- Important for consistent pagination
$function$
;

CREATE OR REPLACE FUNCTION public.get_news_articles_paginated(page_limit integer, page_offset integer)
 RETURNS TABLE(id bigint, created_at timestamp with time zone, title text, url text, description text, category text, media_url text, publish_date timestamp with time zone, source text)
 LANGUAGE sql
AS $function$
SELECT
  na.id,
  na.created_at,
  na.title,
  na.url,
  na.description,
  na.category,
  na.media_url,
  na.publish_date,
  na.source
FROM public.news_articles na
ORDER BY na.id
LIMIT page_limit OFFSET page_offset;
$function$
;


