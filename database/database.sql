-- Adminer 4.8.1 MySQL 11.8.6-MariaDB-5 from Ubuntu dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;

DROP TABLE IF EXISTS `chests`;
CREATE TABLE `chests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL COMMENT 'ID của chủ nhân rương đồ',
  `item_id` int(11) NOT NULL COMMENT 'ID của món đồ trong bảng items',
  `is_use` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0: cất trong rương, 1: đang mặc/sử dụng',
  `is_show` int(11) NOT NULL DEFAULT 1 COMMENT '1: hiển thị, 0: ẩn',
  `date_expired` datetime NOT NULL DEFAULT '2000-01-01 00:00:00' COMMENT 'Ngày hết hạn, mặc định là vĩnh viễn',
  PRIMARY KEY (`id`),
  KEY `index_user_id` (`user_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `chests_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chests_ibfk_3` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='Hành trang cá nhân của người chơi';


DROP TABLE IF EXISTS `dial_lucky`;
CREATE TABLE `dial_lucky` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `item_id` int(11) NOT NULL COMMENT 'ID vật phẩm trúng thưởng',
  `xu` tinyint(4) NOT NULL DEFAULT 0 COMMENT 'Quay bằng Xu (1: Có, 0: Không)',
  `luong` tinyint(4) NOT NULL DEFAULT 0 COMMENT 'Quay bằng Lượng (1: Có, 0: Không)',
  `free` tinyint(4) NOT NULL DEFAULT 0 COMMENT 'Quay Miễn Phí (1: Có, 0: Không)',
  `ratio` tinyint(4) NOT NULL DEFAULT 100 COMMENT 'Tỉ lệ trúng thưởng',
  PRIMARY KEY (`id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `dial_lucky_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='Bảng phần thưởng Vòng quay may mắn';


DROP TABLE IF EXISTS `farm_image_data`;
CREATE TABLE `farm_image_data` (
  `id` int(11) NOT NULL COMMENT 'ID khung cắt',
  `image_id` int(11) DEFAULT NULL COMMENT 'ID ảnh gốc',
  `x` int(11) DEFAULT NULL,
  `y` int(11) DEFAULT NULL,
  `w` int(11) DEFAULT NULL,
  `h` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;


DROP TABLE IF EXISTS `foods`;
CREATE TABLE `foods` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL COMMENT 'Tên món ăn',
  `description` varchar(255) NOT NULL COMMENT 'Mô tả món ăn',
  `img` int(11) NOT NULL COMMENT 'ID Hình ảnh (Sprite)',
  `shop` int(11) NOT NULL COMMENT 'ID Shop bán món này',
  `percent_health` int(11) NOT NULL DEFAULT 0 COMMENT 'Phần trăm thể lực hồi phục',
  `price` int(11) NOT NULL COMMENT 'Giá bán bằng Xu',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;


DROP TABLE IF EXISTS `giaodich_logs`;
CREATE TABLE `giaodich_logs` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user` int(11) NOT NULL DEFAULT 0 COMMENT 'ID người dùng',
  `transID` varchar(50) DEFAULT NULL COMMENT 'Mã giao dịch',
  `type` varchar(20) NOT NULL DEFAULT '0' COMMENT 'Loại giao dịch (Nạp xu, Mua đồ, v.v.)',
  `amount` int(11) NOT NULL DEFAULT 0 COMMENT 'Số tiền / Giá trị',
  `log` text NOT NULL COMMENT 'Chi tiết nhật ký',
  `status` varchar(20) DEFAULT 'SUCCESS' COMMENT 'Trạng thái',
  `time` varchar(50) NOT NULL DEFAULT '0' COMMENT 'Thời gian giao dịch',
  PRIMARY KEY (`id`),
  KEY `user_index` (`user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='Lưu trữ biến động số dư và giao dịch';


DROP TABLE IF EXISTS `giftcode`;
CREATE TABLE `giftcode` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL COMMENT 'Mã Code (Ví dụ: TANTHU2026)',
  `message` varchar(255) DEFAULT NULL COMMENT 'Lời chúc khi nhập code',
  `data` text NOT NULL COMMENT 'JSON chứa ID phần thưởng',
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Thời gian bắt đầu',
  `end_time` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Thời gian kết thúc',
  `num` int(11) NOT NULL DEFAULT 1 COMMENT 'Số lượng người có thể nhập',
  `create_by` int(11) NOT NULL DEFAULT 0 COMMENT 'Admin nào tạo mã này',
  `create_time` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='Danh sách mã quà tặng (Giftcode)';


DROP TABLE IF EXISTS `giftcode_use`;
CREATE TABLE `giftcode_use` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` int(11) NOT NULL COMMENT 'ID người nhập',
  `giftcode_id` int(11) NOT NULL COMMENT 'ID của mã giftcode',
  `time` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Thời điểm nhập',
  PRIMARY KEY (`id`),
  KEY `user_index` (`user`),
  KEY `giftcode_index` (`giftcode_id`),
  CONSTRAINT `fk_giftcode_use_code` FOREIGN KEY (`giftcode_id`) REFERENCES `giftcode` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_giftcode_use_user` FOREIGN KEY (`user`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='Sử dụng mã quà tặng';


DROP TABLE IF EXISTS `gioithieu`;
CREATE TABLE `gioithieu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` int(11) NOT NULL COMMENT 'ID người được mời',
  `user_ref` int(11) NOT NULL COMMENT 'ID người gửi lời mời',
  `ip` varchar(50) NOT NULL DEFAULT '0.0.0.0' COMMENT 'IP chống gian lận clone nick',
  `date` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fk_gioithieu_user` (`user`),
  KEY `fk_gioithieu_ref` (`user_ref`),
  CONSTRAINT `fk_gioithieu_ref` FOREIGN KEY (`user_ref`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_gioithieu_user` FOREIGN KEY (`user`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='Nhật ký giới thiệu bạn bè';


DROP TABLE IF EXISTS `image_data`;
CREATE TABLE `image_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính',
  `item_id` int(11) NOT NULL COMMENT 'ID của vật phẩm',
  `image_id` int(11) NOT NULL COMMENT 'ID của tấm ảnh lớn (Sprite Sheet)',
  `x` int(11) NOT NULL COMMENT 'Tọa độ X trên ảnh lớn',
  `y` int(11) NOT NULL COMMENT 'Tọa độ Y trên ảnh lớn',
  `w` int(11) NOT NULL COMMENT 'Chiều rộng (Width) khung cắt',
  `h` int(11) NOT NULL COMMENT 'Chiều cao (Height) khung cắt',
  PRIMARY KEY (`id`),
  KEY `idx_item` (`item_id`),
  KEY `idx_image` (`image_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='Bản đồ cắt ảnh Sprite Sheet cho đồ họa Game';


DROP TABLE IF EXISTS `items`;
CREATE TABLE `items` (
  `id` int(11) NOT NULL,
  `coin` int(11) NOT NULL DEFAULT 0 COMMENT 'Giá mua bằng Xu',
  `gold` smallint(6) NOT NULL DEFAULT 0 COMMENT 'Giá mua bằng Lượng',
  `type` smallint(6) NOT NULL COMMENT 'Phân loại đồ (Tóc, Áo, Quần, Mắt,...)',
  `icon` smallint(6) NOT NULL COMMENT 'ID Icon trong hành trang',
  `name` varchar(200) NOT NULL DEFAULT '' COMMENT 'Tên vật phẩm',
  `sell` tinyint(4) DEFAULT NULL COMMENT 'Loại hình bán/giao dịch',
  `expired_day` tinyint(4) NOT NULL DEFAULT 0 COMMENT 'Thời hạn sử dụng (0 = vĩnh viễn)',
  `zorder` tinyint(4) DEFAULT NULL COMMENT 'Thứ tự vẽ đè layer (Layering order)',
  `gender` tinyint(4) DEFAULT NULL COMMENT '0: Nam/Nữ, 1: Nam, 2: Nữ',
  `level` tinyint(4) DEFAULT NULL COMMENT 'Cấp độ yêu cầu để mặc',
  `animation` text DEFAULT NULL COMMENT 'Mảng JSON chứa các khung hình chuyển động (Animation Frames)',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='Bảng dữ liệu gốc của mọi vật phẩm thời trang';


DROP TABLE IF EXISTS `item_image_data`;
CREATE TABLE `item_image_data` (
  `id` int(11) NOT NULL COMMENT 'ID Khung hình/Cắt ảnh',
  `image_id` int(11) DEFAULT NULL COMMENT 'ID của file ảnh gốc',
  `x` int(11) DEFAULT NULL COMMENT 'Tọa độ cắt X',
  `y` int(11) DEFAULT NULL COMMENT 'Tọa độ cắt Y',
  `w` int(11) DEFAULT NULL COMMENT 'Chiều rộng khung cắt',
  `h` int(11) DEFAULT NULL COMMENT 'Chiều cao khung cắt',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='Bảng dữ liệu tọa độ cắt ảnh Sprite Sheet';


DROP TABLE IF EXISTS `map_item`;
CREATE TABLE `map_item` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Mã định danh duy nhất của vật phẩm trên map',
  `type_id` int(11) NOT NULL COMMENT 'ID của loại vật phẩm (liên kết với bảng map_item_type)',
  `type` int(11) NOT NULL DEFAULT 0 COMMENT 'Phân loại lớp vẽ (ví dụ: đồ trên tường, đồ dưới đất)',
  `x` int(11) NOT NULL COMMENT 'Tọa độ ô X trên lưới Isometric',
  `y` int(11) NOT NULL COMMENT 'Tọa độ ô Y trên lưới Isometric',
  `map_id` int(11) NOT NULL COMMENT 'ID của khu vực/map chứa vật phẩm này',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='Bảng lưu vị trí thực tế của từng vật phẩm trên bản đồ';


DROP TABLE IF EXISTS `map_item_type`;
CREATE TABLE `map_item_type` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL COMMENT 'Tên vật phẩm nội thất/map',
  `description` varchar(255) DEFAULT '' COMMENT 'Mô tả chi tiết',
  `image` smallint(6) NOT NULL COMMENT 'ID của Sprite hình ảnh',
  `icon` tinyint(4) NOT NULL COMMENT 'ID Icon trong túi đồ',
  `price_coin` int(11) NOT NULL DEFAULT 0 COMMENT 'Giá mua bằng Xu',
  `price_gold` int(11) NOT NULL DEFAULT 0 COMMENT 'Giá mua bằng Lượng',
  `buy` int(11) NOT NULL DEFAULT 1 COMMENT '1: Có thể mua, 0: Không thể mua',
  `dx` smallint(6) NOT NULL DEFAULT 0 COMMENT 'Sai số trục X khi vẽ',
  `dy` smallint(6) NOT NULL DEFAULT 0 COMMENT 'Sai số trục Y khi vẽ',
  `position` text NOT NULL COMMENT 'JSON Mảng lưới chiếm dụng',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='Bảng dữ liệu các vật phẩm được phép đặt xuống bản đồ';


DROP TABLE IF EXISTS `media`;
CREATE TABLE `media` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `post_id` int(11) DEFAULT NULL,
  `file_url` varchar(255) NOT NULL,
  `media_type` varchar(50) DEFAULT 'image',
  PRIMARY KEY (`id`),
  KEY `post_id` (`post_id`),
  CONSTRAINT `media_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `npc`;
CREATE TABLE `npc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL COMMENT 'Tên hiển thị của NPC',
  `items` text NOT NULL COMMENT 'Mảng JSON chứa ID vật phẩm NPC bán hoặc tương tác',
  `map` int(11) NOT NULL COMMENT 'ID của Map mà NPC đứng',
  `x` int(11) NOT NULL DEFAULT 0 COMMENT 'Tọa độ X trên map',
  `y` int(11) NOT NULL DEFAULT 0 COMMENT 'Tọa độ Y trên map',
  `star` int(11) NOT NULL DEFAULT 0 COMMENT 'ID Hình ảnh/Icon hiển thị của NPC',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='Bảng lưu trữ vị trí và cửa hàng của NPC';


DROP TABLE IF EXISTS `players`;
CREATE TABLE `players` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `last_online` datetime NOT NULL DEFAULT '2000-01-01 00:00:00',
  `is_online` tinyint(1) NOT NULL DEFAULT 0,
  `client_id` int(11) NOT NULL DEFAULT 0,
  `xu` int(11) NOT NULL DEFAULT 20000,
  `luong` int(11) NOT NULL DEFAULT 0,
  `luong_khoa` int(11) NOT NULL DEFAULT 0,
  `xeng` int(11) NOT NULL DEFAULT 0,
  `clan_id` int(11) NOT NULL DEFAULT 0,
  `star` int(11) NOT NULL DEFAULT -1,
  `items` varchar(5000) NOT NULL DEFAULT '[]',
  `gender` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0: None, 1: Nam, 2: Nữ',
  `level_main` int(11) NOT NULL DEFAULT 1,
  `exp_main` int(11) NOT NULL DEFAULT 0,
  `exp_farm` int(11) NOT NULL DEFAULT 0,
  `friendly` tinyint(4) NOT NULL DEFAULT 100,
  `crazy` tinyint(4) NOT NULL DEFAULT 0,
  `stylish` tinyint(4) NOT NULL DEFAULT 0,
  `happy` tinyint(4) NOT NULL DEFAULT 100,
  `hunger` tinyint(4) NOT NULL DEFAULT 0,
  `chest_slot` int(11) NOT NULL DEFAULT 10,
  `chest_home_slot` int(11) NOT NULL DEFAULT 10,
  `chests` text NOT NULL,
  `wearing` text NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `unique_user_id` (`user_id`) USING BTREE,
  CONSTRAINT `players_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='Bảng lưu dữ liệu chi tiết của người chơi';


DROP TABLE IF EXISTS `post`;
CREATE TABLE `post` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `content` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `post_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `posts`;
CREATE TABLE `posts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `content` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `attached_media` varchar(255) DEFAULT NULL,
  `media_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `settings`;
CREATE TABLE `settings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL COMMENT 'Tên biến cấu hình',
  `value` text DEFAULT NULL COMMENT 'Giá trị cấu hình',
  PRIMARY KEY (`id`),
  UNIQUE KEY `NAME_UNIQUE` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='Bảng cấu hình linh hoạt cho hệ thống Game';


DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `fullname` varchar(100) DEFAULT NULL,
  `avatar_url` varchar(255) DEFAULT '',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `email` varchar(100) DEFAULT NULL,
  `password_hash` varchar(255) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `cccd` varchar(20) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `address` text DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT 0,
  `otp_code` varchar(10) DEFAULT NULL,
  `role` smallint(6) NOT NULL DEFAULT -1 COMMENT 'Chức vụ trong game (-1: Mặc định, 1: Admin, v.v.)',
  `ban` varchar(500) DEFAULT NULL COMMENT 'Lý do khóa tài khoản',
  `active` int(11) NOT NULL DEFAULT 0 COMMENT 'Trạng thái kích hoạt (0: Chưa, 1: Đã kích hoạt)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `cccd` (`cccd`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2026-06-25 05:06:14