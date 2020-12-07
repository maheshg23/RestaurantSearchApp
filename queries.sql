-- List the top 5 restaurants based on the average user reviews 

SELECT res.id, res.name, avg_rating 
FROM restaurants as res JOIN 
    (   SELECT res_id, ROUND(avg(rating),3) AS avg_rating FROM reviews 
        GROUP BY res_id 
    ) AS reviews_rating 
ON res.id = reviews_rating.res_id 
ORDER BY reviews_rating.avg_rating DESC 
LIMIT 5;

-- List all reviews and photos posted for each restaurant along with the username who posted it.

SELECT res.id, res.name, r.rid, r.text, u.uid, u.username FROM restaurants AS res, reviews AS r, users AS u
WHERE res.id = r.res_id and u.uid = r.user_id
ORDER BY res.id;

SELECT res.id, res.name, p.pid, p.url, u.uid, u.username FROM restaurants AS res, photos AS p, users AS u
WHERE res.id = p.res_id AND u.uid = p.user_id
ORDER BY res.id;

-- Search with Restaurant Name, City, Country, Status, Tags, Payment Method

SELECT DISTINCT res.id, res.name, l.city, l.country, s.name, pm.name, * 
FROM restaurants AS res, status AS s, location AS l, 
        restaurant_payments_mapping AS rpm, payment_methods AS pm,
        restaurant_tags_mapping as rtm, tags AS t
where   res.status = s.sid AND 
        res.location = l.lid AND 
        res.id = rpm.res_id AND 
        rpm.payment_id = pm.pmid AND 
        res.id = rtm.res_id AND
        rtm.tag_id = t.tid;


-- Show 10 users with the maximum number of reviews posted

SELECT u.uid, u.name, u.username, reviews_user.review_count 
FROM users AS u, 
    (   SELECT user_id, COUNT(*) as review_count
        FROM reviews 
        GROUP BY user_id
    ) AS reviews_user
WHERE u.uid = reviews_user.user_id 
ORDER BY review_count DESC 
LIMIT 10;

-- Show the Restaurant Owners who give reviews to their own restaurants
SELECT d.rid, d.res_name, d.user_id, d.rating, * 
FROM users u, 
    (   SELECT r.id AS rid, r.name AS res_name, r.owner_id AS user_id, AVG(rv.rating) AS rating 
        FROM restaurants r, reviews rv 
        WHERE r.id = rv.res_id AND r.owner_id = rv.user_id 
        GROUP BY r.owner_id, r.id
    ) d 
WHERE d.user_id = u.uid;


-- List the users who have posted both photos and reviews along with the count of the number of photos and reviews posted by them
SELECT u.uid, u.name, COUNT(DISTINCT rv.rid) AS review_count, COUNT(DISTINCT p.pid) AS photo_count 
FROM users u, reviews rv, photos p 
WHERE u.uid = rv.user_id AND u.uid = p.user_id 
GROUP BY u.uid 
ORDER BY review_count, photo_count DESC;


SELECT r.user_id, COUNT(r.rid) 
FROM photos p, reviews r 
WHERE r.user_id = p.user_id 
GROUP BY r.user_id 
ORDER BY COUNT(r.rid) DESC;