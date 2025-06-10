set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.get_unlinked_articles(created_after timestamp with time zone, row_limit integer)
 RETURNS SETOF news_articles
 LANGUAGE sql
 STABLE
AS $function$
    SELECT *
    FROM news_articles na
    WHERE na.id NOT IN (SELECT news_article_id FROM news_article_sentiments)
      AND na.created_at > created_after
      AND na.hidden IS NULL
    LIMIT row_limit;
$function$
;


