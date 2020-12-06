-- List the top 5 restaurants based on the average user reviews 

SELECT * FROM restaurants JOIN (
    SELECT res_id, avg(rating) AS avg_rating FROM reviews
    GROUP BY res_id
) AS reviews 
ON restaurants.id = reviews.res_id 
ORDER BY avg_rating DESC 
LIMIT 5;

-- List all reviews and photos posted for each restaurant along with the username who posted it.

SELECT res.id, res.name, r.rid, r.text, u.uid, u.username FROM restaurants AS res, reviews AS r, users AS u
WHERE res.id = r.res_id and u.uid = r.user_id
ORDER BY res.id;

SELECT res.id, res.name, p.pid, p.url, u.uid, u.username FROM restaurants AS res, photos AS p, users AS u
WHERE res.id = p.res_id AND u.uid = p.user_id
ORDER BY res.id;

