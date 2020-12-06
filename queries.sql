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

-- Search with Restaurant Name, City, Country, Status, Tags, Payment Method

SELECT * FROM   restaurants AS res, status AS s, location AS l, 
                restaurant_payments_mapping AS rpm, payment_methods AS pm,
                restaurant_tags_mapping as rtm, tags AS t
where   res.status = s.sid AND 
        res.location = l.lid AND 
        res.id = rpm.res_id AND 
        rpm.payment_id = pm.pmid AND 
        res.id = rtm.res_id AND
        rtm.tag_id = t.tid AND
        (res.name = 'Indian' OR 
        l.city = 'Seattle' OR
        l.country = 'USA' OR
        s.name = 'Open' OR
        t.name = 'Indian' OR
        pm.name = 'Cash' OR
        );

SELECT * FROM   restaurants AS res, status AS s, location AS l, 
                restaurant_payments_mapping AS rpm, payment_methods AS pm,
                restaurant_tags_mapping as rtm, tags AS t
where   res.status = s.sid AND 
        res.location = l.lid AND 
        res.id = rpm.res_id AND 
        rpm.payment_id = pm.pmid AND 
        res.id = rtm.res_id AND
        rtm.tag_id = t.tid AND
        l.city = 'Seattle';

