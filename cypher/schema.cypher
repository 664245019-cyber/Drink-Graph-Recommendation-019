// ==========================================
// 1. สร้าง User จำนวน 10 คน (รวมถึง "หนึ่ง")
// ==========================================
CREATE (u1:User {name: 'หนึ่ง'})
CREATE (u2:User {name: 'กอล์ฟ'})
CREATE (u3:User {name: 'แบงค์'})
CREATE (u4:User {name: 'บี'})
CREATE (u5:User {name: 'มายด์'})
CREATE (u6:User {name: 'ปาล์ม'})
CREATE (u7:User {name: 'นัท'})
CREATE (u8:User {name: 'ท็อป'})
CREATE (u9:User {name: 'โบว์'})
CREATE (u10:User {name: 'เต้ย'});

// ==========================================
// 2. สร้างความสัมพันธ์ความเป็นเพื่อน (FRIEND_WITH)
// ==========================================
MATCH (u1:User {name: 'หนึ่ง'}), (u2:User {name: 'กอล์ฟ'}) MERGE (u1)-[:FRIEND_WITH]->(u2);
MATCH (u1:User {name: 'หนึ่ง'}), (u3:User {name: 'แบงค์'}) MERGE (u1)-[:FRIEND_WITH]->(u3);
MATCH (u1:User {name: 'หนึ่ง'}), (u6:User {name: 'ปาล์ม'}) MERGE (u1)-[:FRIEND_WITH]->(u6);
MATCH (u2:User {name: 'กอล์ฟ'}), (u4:User {name: 'บี'}) MERGE (u2)-[:FRIEND_WITH]->(u4);
MATCH (u3:User {name: 'แบงค์'}), (u5:User {name: 'มายด์'}) MERGE (u3)-[:FRIEND_WITH]->(u5);
MATCH (u6:User {name: 'ปาล์ม'}), (u7:User {name: 'นัท'}) MERGE (u6)-[:FRIEND_WITH]->(u7);
MATCH (u7:User {name: 'นัท'}), (u8:User {name: 'ท็อป'}) MERGE (u7)-[:FRIEND_WITH]->(u8);
MATCH (u8:User {name: 'ท็อป'}), (u9:User {name: 'โบว์'}) MERGE (u8)-[:FRIEND_WITH]->(u9);
MATCH (u9:User {name: 'โบว์'}), (u10:User {name: 'เต้ย'}) MERGE (u9)-[:FRIEND_WITH]->(u10);

// ==========================================
// 3. สร้างเมนูเครื่องดื่ม 10 เมนู (ผูกกับไฟล์รูปในโฟลเดอร์ images/)
// ==========================================
CREATE (d1:Drink {name: 'ชานมไข่มุก', price: 65, image: 'images/d1.jpg'})
CREATE (d2:Drink {name: 'มัทฉะลาเต้', price: 80, image: 'images/d2.jpg'})
CREATE (d3:Drink {name: 'โกโก้เย็น', price: 70, image: 'images/d3.jpg'})
CREATE (d4:Drink {name: 'อิตาเลียนโซดา', price: 55, image: 'images/d4.jpg'})
CREATE (d5:Drink {name: 'กาแฟดำ', price: 60, image: 'images/d5.jpg'})
CREATE (d6:Drink {name: 'นมสดคาราเมล', price: 65, image: 'images/d6.jpg'})
CREATE (d7:Drink {name: 'ชาไทย', price: 50, image: 'images/d7.jpg'})
CREATE (d8:Drink {name: 'สมูทตี้สตอเบอร์รี่', price: 90, image: 'images/d8.jpg'})
CREATE (d9:Drink {name: 'ชาเขียวมะลิ', price: 45, image: 'images/d9.jpg'})
CREATE (d10:Drink {name: 'โอวัลตินภูเขาไฟ', price: 75, image: 'images/d10.jpg'});

// ==========================================
// 4. สร้างประวัติการสั่งซื้อ (ORDERED) เพื่อเชื่อมโยงความชอบ
// ==========================================
// หนึ่ง เคยสั่งชานมไข่มุก
MATCH (u:User {name: 'หนึ่ง'}), (d:Drink {name: 'ชานมไข่มุก'}) MERGE (u)-[:ORDERED]->(d);

// เพื่อนๆ ของหนึ่ง เคยสั่งเมนูเหล่านี้
MATCH (u:User {name: 'กอล์ฟ'}), (d:Drink {name: 'มัทฉะลาเต้'}) MERGE (u)-[:ORDERED]->(d);
MATCH (u:User {name: 'กอล์ฟ'}), (d:Drink {name: 'ชาไทย'}) MERGE (u)-[:ORDERED]->(d);
MATCH (u:User {name: 'แบงค์'}), (d:Drink {name: 'โกโก้เย็น'}) MERGE (u)-[:ORDERED]->(d);
MATCH (u:User {name: 'แบงค์'}), (d:Drink {name: 'อิตาเลียนโซดา'}) MERGE (u)-[:ORDERED]->(d);
MATCH (u:User {name: 'ปาล์ม'}), (d:Drink {name: 'สมูทตี้สตอเบอร์รี่'}) MERGE (u)-[:ORDERED]->(d);
MATCH (u:User {name: 'ปาล์ม'}), (d:Drink {name: 'นมสดคาราเมล'}) MERGE (u)-[:ORDERED]->(d);
MATCH (u:User {name: 'นัท'}), (d:Drink {name: 'กาแฟดำ'}) MERGE (u)-[:ORDERED]->(d);
MATCH (u:User {name: 'ท็อป'}), (d:Drink {name: 'ชาเขียวมะลิ'}) MERGE (u)-[:ORDERED]->(d);
MATCH (u:User {name: 'โบว์'}), (d:Drink {name: 'โอวัลตินภูเขาไฟ'}) MERGE (u)-[:ORDERED]->(d);