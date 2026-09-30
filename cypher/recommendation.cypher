// แทนที่ชื่อ 'หนึ่ง' ด้วยตัวแปรชื่อ User ที่ผู้ใช้เลือกในระบบหน้าเว็บ
MATCH (u:User {name: 'หนึ่ง'})-[:FRIEND_WITH]-(friend:User)-[:ORDERED]->(d:Drink)
WHERE NOT (u)-[:ORDERED]->(d)
RETURN DISTINCT d.name AS drink_name, d.price AS price, d.image AS image_path, friend.name AS friend_name