GRANT CREATE ROLE TO register;
CREATE ROLE game_user_role;
GRANT CREATE SESSION TO game_user_role;
GRANT EXECUTE ON register.CREATE_GAME TO game_user_role;
GRANT EXECUTE ON register.GET_GAME_RULES TO game_user_role;
GRANT EXECUTE ON register.JOIN_GAME TO game_user_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON register.GAMES TO game_user_role;
GRANT SELECT ON register.LEADERBOARD TO game_user_role;
GRANT SELECT, INSERT, DELETE ON register.PLAYERS TO game_user_role;
GRANT SELECT, INSERT, UPDATE ON register.PLAYER_STATES TO game_user_role;
GRANT SELECT ON register.BIG_WORDS TO game_user_role;
GRANT SELECT ON register.SMALL_WORDS TO game_user_role;
GRANT SELECT, INSERT ON register.GAME_MOVES TO game_user_role;
GRANT SELECT, INSERT, DELETE ON register.GAME_NOTIFICATIONS TO game_user_role;
GRANT EXECUTE ON register.submit_word_and_pass_turn TO game_user_role;
GRANT EXECUTE ON register.skip_turn TO game_user_role;



GRANT CREATE JOB TO REGISTER;



CREATE OR REPLACE FUNCTION ENCRYPT_PASSWORD(p_password IN VARCHAR2)
RETURN VARCHAR2
AS
    v_raw_input   RAW(2000);
    v_hashed_raw  RAW(32);
BEGIN
    -- Проверка длины пароля
    IF LENGTH(p_password) > 1000 THEN
        RAISE_APPLICATION_ERROR(-20010, 'Пароль слишком длинный.');
    END IF;

    -- Преобразуем строку в RAW
    v_raw_input := UTL_I18N.STRING_TO_RAW(p_password, 'AL32UTF8');

    -- Хешируем через SHA-256
    v_hashed_raw := DBMS_CRYPTO.HASH(v_raw_input, DBMS_CRYPTO.HASH_SH256);

    -- Возвращаем HEX
    RETURN LOWER(RAWTOHEX(v_hashed_raw));
END ENCRYPT_PASSWORD;



CREATE OR REPLACE PROCEDURE REGISTER(
    p_username IN VARCHAR2,
    p_password IN VARCHAR2,
    p_confirm_password IN VARCHAR2
)
AS
    v_exists NUMBER;
    v_errors VARCHAR2(4000) := '';
    v_sql VARCHAR2(1000);
BEGIN
    -- Проверки пароля
    IF p_password != p_confirm_password THEN
        v_errors := v_errors || '- Пароли не совпадают.' || CHR(10);
    END IF;

    IF LENGTH(p_password) < 8 THEN
        v_errors := v_errors || '- Пароль слишком короткий (минимум 8 символов).' || CHR(10);
    END IF;

    IF NOT REGEXP_LIKE(p_password, '[[:lower:]]', 'c') THEN
        v_errors := v_errors || '- Пароль должен содержать минимум 1 строчную букву.' || CHR(10);
    END IF;

    IF NOT REGEXP_LIKE(p_password, '[[:upper:]]', 'c') THEN
        v_errors := v_errors || '- Пароль должен содержать минимум 1 заглавную букву.' || CHR(10);
    END IF;

    IF NOT REGEXP_LIKE(p_password, '[!@#$%^&*(),.?":{}|<>]') THEN
        v_errors := v_errors || '- Пароль должен содержать минимум 1 спецсимвол.' || CHR(10);
    END IF;

    IF LENGTH(TRIM(v_errors)) > 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Ошибки при регистрации:' || CHR(10) || v_errors);
    END IF;

    -- Проверка существования пользователя
    SELECT COUNT(*) INTO v_exists
    FROM USERS
    WHERE username = p_username;

    IF v_exists > 0 THEN
        RAISE_APPLICATION_ERROR(-20002, 'Пользователь с таким именем уже существует.');
    END IF;

    -- Добавление в таблицу USERS
    INSERT INTO USERS (username, password)
    VALUES (p_username, ENCRYPT_PASSWORD(p_password));

    BEGIN
        -- Создание пользователя Oracle
        v_sql := 'CREATE USER ' || LOWER(p_username) || ' IDENTIFIED BY "' || p_password || '"';
        EXECUTE IMMEDIATE v_sql;

		EXECUTE IMMEDIATE 'GRANT game_user_role TO ' || LOWER(p_username);
		EXECUTE IMMEDIATE 'ALTER USER ' || LOWER(p_username) || ' DEFAULT ROLE game_user_role';
			
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Ошибка при создании пользователя: ' || SQLERRM);
    END;

    COMMIT;
END REGISTER;


CREATE OR REPLACE TRIGGER trg_first_login
AFTER INSERT ON users  -- Триггер срабатывает после вставки нового пользователя в таблицу users
FOR EACH ROW
BEGIN
    -- Вставка нового пользователя с начальным количеством очков 0 в таблицу leaderboard
    INSERT INTO leaderboard (username, score)
    VALUES (:NEW.username, 0);
END;




CREATE OR REPLACE PROCEDURE LOGIN(p_username IN VARCHAR2, p_password IN VARCHAR2) AS
    v_stored_password VARCHAR2(2000);
    v_encrypted_password VARCHAR2(2000);
BEGIN
    -- Получаем хэшированный пароль пользователя из базы данных
    SELECT password
    INTO v_stored_password
    FROM USERS
    WHERE username = p_username;

    -- Хэшируем введенный пароль
    v_encrypted_password := ENCRYPT_PASSWORD(p_password);

    -- Сравниваем хэшированные пароли
    IF v_stored_password != v_encrypted_password THEN
        RAISE_APPLICATION_ERROR(-20008, 'Неверный пароль.');
    END IF;

    -- Если все в порядке, можно выполнить дальнейшие действия
    DBMS_OUTPUT.PUT_LINE('Авторизация прошла успешно.');
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE_APPLICATION_ERROR(-20007, 'Пользователь не найден.');
END LOGIN;






CREATE OR REPLACE PROCEDURE register.GET_GAME_RULES(
    p_username IN VARCHAR2,
    p_rules OUT CLOB
)
AS
BEGIN
        p_rules := 'Добро пожаловать в игру! Правила игры следующие: ' || CHR(10) ||
                   '1. Система выдает первоначальное слово из 12-15 букв.' || CHR(10) ||
                   '2. Игроки по очереди составляют слова из букв этого слова.' || CHR(10) ||
                   '3. Слово должно существовать в словаре игры.' || CHR(10) ||
                   '4. Слово не должно повторяться в течение игры.' || CHR(10) ||
                   '5. Игра оканчивается, когда все игроки по очереди пропускают ход.' || CHR(10) ||
                   '6. Выигрывает тот игрок, у которого общее количество букв в составленных словах больше.' || CHR(10) ||
                   'Удачи в игре!' || CHR(10);
    END GET_GAME_RULES;







CREATE OR REPLACE PROCEDURE CREATE_GAME(
    p_owner_username IN VARCHAR2,
    p_room_name      IN VARCHAR2,
    p_max_players    IN NUMBER,
    p_password       IN VARCHAR2,
    p_turn_time_min  IN NUMBER,
    p_is_vs_bot      IN NUMBER
)
AS
    v_game_id NUMBER;
    v_sql      VARCHAR2(4000);
BEGIN
    -- Вставка данных в таблицу GAMES
    INSERT INTO games (
        owner_username,
        room_name,
        max_players,
        password_hash,
        created_by,
        turn_time_minutes,
        is_vs_bot
    ) 
    VALUES (
        p_owner_username,
        p_room_name,
        p_max_players,
        CASE WHEN p_password IS NOT NULL THEN p_password ELSE NULL END,
        p_owner_username,
        p_turn_time_min,
        p_is_vs_bot
    ) RETURNING game_id INTO v_game_id;

    -- Динамическое создание таблицы для игроков этой игры
    v_sql := 'CREATE GLOBAL TEMPORARY TABLE game_' || p_room_name || '_players (' ||
             'player_id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY, ' ||
             'player_username VARCHAR2(50), ' ||
             'status VARCHAR2(20) DEFAULT ''waiting'', ' ||
             'word VARCHAR2(255) DEFAULT NULL, ' ||
             'game_id NUMBER' ||
             ') ON COMMIT DELETE ROWS';
    
    EXECUTE IMMEDIATE v_sql;

    -- Добавление первого игрока (создателя игры) в эту таблицу
    v_sql := 'INSERT INTO game_' || p_room_name || '_players (player_username, status, word, game_id) ' ||
             'VALUES (:owner_username, ''waiting'', NULL, :game_id)';
    EXECUTE IMMEDIATE v_sql USING p_owner_username, v_game_id;
    
    COMMIT;
END;






CREATE OR REPLACE PROCEDURE create_game_players_table(p_game_id IN NUMBER, p_room_name IN VARCHAR2) AS
    v_word VARCHAR2(255);
BEGIN
    -- Получаем случайное слово из таблицы big_words
    SELECT word INTO v_word
    FROM register.big_words
    WHERE ROWNUM = 1;  -- Выбираем первое слово (можно модифицировать логику выбора)

    -- Создаем временную таблицу для игроков с именем, содержащим название игры
    EXECUTE IMMEDIATE 'CREATE GLOBAL TEMPORARY TABLE game_' || p_room_name || '_players (
        player_id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        player_username VARCHAR2(50),
        status VARCHAR2(20) DEFAULT ''waiting'',
        word VARCHAR2(255) DEFAULT ''' || v_word || ''',
        game_id NUMBER DEFAULT ' || p_game_id || '
    ) ON COMMIT DELETE ROWS';

    -- Вставляем первого игрока (создателя игры) в таблицу
    EXECUTE IMMEDIATE 'INSERT INTO game_' || p_room_name || '_players (player_username, status, word, game_id) 
        VALUES (:owner_username, ''waiting'', ''' || v_word || ''', :game_id)'
    USING :NEW.owner_username, p_game_id;
END create_game_players_table;








BEGIN
    DBMS_SCHEDULER.CREATE_JOB (
        job_name        => 'CHECK_ACTIVE_GAMES',
        job_type        => 'PLSQL_BLOCK',
        job_action      => 'BEGIN 
                              FOR game IN (SELECT game_id FROM register.games WHERE status = ''in_progress'') 
                              LOOP 
                                  register.check_turn_time(game.game_id); 
                              END LOOP; 
                           END;',
        start_date      => SYSTIMESTAMP,
        repeat_interval => 'FREQ=MINUTELY;INTERVAL=1',
        enabled         => TRUE,
        comments        => 'Проверка активных игр на истечение времени хода');
END;
















CREATE OR REPLACE PACKAGE register.game_timer_pkg AS
    -- Проверка времени хода (вызывается по таймеру)
    PROCEDURE check_turn_time(game_id IN NUMBER);
    
    -- Проверка условий завершения игры
    FUNCTION should_end_game(game_id IN NUMBER) RETURN NUMBER;
    
    -- Передача хода следующему игроку
    PROCEDURE pass_turn(game_id IN NUMBER);
    
    -- Завершение игры
    PROCEDURE end_game(game_id IN NUMBER);
END game_timer_pkg;







CREATE OR REPLACE PACKAGE BODY register.game_timer_pkg AS
    ------------------------------------------------------------------
    -- check_turn_time: Проверка времени хода (вызывается по таймеру)
    ------------------------------------------------------------------
    PROCEDURE check_turn_time(game_id IN NUMBER) IS
        v_game_status VARCHAR2(20);
        v_current_player VARCHAR2(100);
        v_turn_end_time TIMESTAMP;
        v_should_end NUMBER;
    BEGIN
        -- Проверяем статус игры и время хода
        SELECT status, current_player, turn_end_time 
        INTO v_game_status, v_current_player, v_turn_end_time
        FROM register.games
        WHERE game_id = check_turn_time.game_id;
    
        IF v_game_status != 'in_progress' THEN
            RETURN;
        END IF;
    
        -- Если время хода истекло, добавляем пропуск
        IF CURRENT_TIMESTAMP > v_turn_end_time THEN
            -- Добавляем запись о пропуске хода
            INSERT INTO register.game_moves 
            (game_id, player_username, word, is_valid, move_time)
            VALUES (game_id, v_current_player, '[Пропуск хода]', 0, CURRENT_TIMESTAMP);
            
            -- Проверяем условия завершения игры
            v_should_end := game_timer_pkg.should_end_game(game_id);
            IF v_should_end = 1 THEN
                game_timer_pkg.end_game(game_id);
            ELSE
                -- Передаем ход следующему игроку
                game_timer_pkg.pass_turn(game_id);
            END IF;
        END IF;
    
    EXCEPTION
        WHEN OTHERS THEN
            NULL;
    END check_turn_time;

    ------------------------------------------------------------------
    -- should_end_game: Проверяет, нужно ли завершать игру
    -- (все игроки по очереди пропустили ход)
    ------------------------------------------------------------------
    FUNCTION should_end_game(game_id IN NUMBER) RETURN NUMBER IS
        v_total_players NUMBER;
        v_last_moves SYS_REFCURSOR;
        v_player_username VARCHAR2(100);
        v_word VARCHAR2(100);
        v_move_time TIMESTAMP;
        v_players_skipped NUMBER := 0;
        v_distinct_players NUMBER := 0;
        v_expected_player_order NUMBER := 0;
        v_current_player_order NUMBER;
        v_correct_order NUMBER := 1;
    BEGIN
        -- Получаем количество игроков
        SELECT COUNT(*) INTO v_total_players
        FROM register.players
        WHERE game_id = should_end_game.game_id;

        -- Проверяем последние N ходов (N = количество игроков)
        OPEN v_last_moves FOR 
            SELECT gm.player_username, gm.word, gm.move_time, p.move_order
            FROM (
                SELECT player_username, word, move_time
                FROM register.game_moves
                WHERE game_id = should_end_game.game_id
                ORDER BY move_time DESC
            ) gm
            JOIN register.players p ON gm.player_username = p.player_username AND p.game_id = should_end_game.game_id
            WHERE ROWNUM <= v_total_players
            ORDER BY gm.move_time DESC;

        -- Проверяем условия:
        -- 1. Все ходы должны быть пропусками
        -- 2. Все игроки должны быть разные
        -- 3. Игроки должны пропускать ход в правильном порядке
        LOOP
            FETCH v_last_moves INTO v_player_username, v_word, v_move_time, v_current_player_order;
            EXIT WHEN v_last_moves%NOTFOUND;

            -- Проверяем, что ход - пропуск
            IF v_word != '[Пропуск хода]' THEN
                v_correct_order := 0;
                EXIT;
            END IF;

            v_players_skipped := v_players_skipped + 1;
            
            -- Проверяем порядок игроков (должны идти по очереди)
            IF v_expected_player_order = 0 THEN
                v_expected_player_order := v_current_player_order;
            ELSE
                -- Ожидаемый следующий игрок
                v_expected_player_order := CASE 
                    WHEN v_expected_player_order < v_total_players THEN v_expected_player_order + 1
                    ELSE 1
                END;
                
                IF v_current_player_order != v_expected_player_order THEN
                    v_correct_order := 0;
                    EXIT;
                END IF;
            END IF;
        END LOOP;

        CLOSE v_last_moves;

        -- Проверяем, что все игроки пропустили ход в правильном порядке
        IF v_players_skipped = v_total_players AND v_correct_order = 1 THEN
            RETURN 1;
        ELSE
            RETURN 0;
        END IF;

    EXCEPTION
        WHEN OTHERS THEN
            IF v_last_moves%ISOPEN THEN
                CLOSE v_last_moves;
            END IF;
            RETURN 0;
    END should_end_game;

    ------------------------------------------------------------------
    -- pass_turn: Передача хода следующему игроку
    ------------------------------------------------------------------
    PROCEDURE pass_turn(game_id IN NUMBER) IS
        v_current_player VARCHAR2(100);
        v_next_player VARCHAR2(100);
        v_turn_time NUMBER;
        v_game_status VARCHAR2(20);
        v_player_count NUMBER;
        v_current_order NUMBER;
    BEGIN
        -- Проверяем статус игры
        SELECT status INTO v_game_status 
        FROM register.games 
        WHERE game_id = pass_turn.game_id;
        
        IF v_game_status != 'in_progress' THEN
            RETURN;
        END IF;
        
        -- Получаем текущего игрока и время хода
        SELECT current_player, turn_time_minutes
        INTO v_current_player, v_turn_time
        FROM register.games
        WHERE game_id = pass_turn.game_id;
        
        -- Находим следующего игрока
        BEGIN
            -- Получаем порядок текущего игрока
            SELECT move_order INTO v_current_order
            FROM register.players
            WHERE game_id = pass_turn.game_id 
            AND player_username = v_current_player;
            
            -- Получаем общее количество игроков
            SELECT COUNT(*) INTO v_player_count
            FROM register.players
            WHERE game_id = pass_turn.game_id;
            
            -- Определяем следующего игрока
            IF v_current_order < v_player_count THEN
                -- Берем следующего по порядку
                SELECT player_username INTO v_next_player
                FROM register.players
                WHERE game_id = pass_turn.game_id 
                AND move_order = v_current_order + 1;
            ELSE
                -- Возвращаемся к первому игроку
                SELECT player_username INTO v_next_player
                FROM register.players
                WHERE game_id = pass_turn.game_id 
                AND move_order = 1;
            END IF;
            
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                SELECT player_username INTO v_next_player
                FROM register.players
                WHERE game_id = pass_turn.game_id
                ORDER BY move_order
                FETCH FIRST 1 ROWS ONLY;
        END;
        
        -- Обновляем текущего игрока и сбрасываем таймер
        UPDATE register.games
        SET current_player = v_next_player,
            start_time = CURRENT_TIMESTAMP,
            turn_end_time = CURRENT_TIMESTAMP + (v_turn_time * INTERVAL '1' MINUTE),
            last_update = CURRENT_TIMESTAMP
        WHERE game_id = pass_turn.game_id;
        
        COMMIT;
        
    EXCEPTION
        WHEN OTHERS THEN
            NULL;
    END pass_turn;

    ------------------------------------------------------------------
    -- end_game: Завершение игры и определение победителя
    ------------------------------------------------------------------
    PROCEDURE end_game(game_id IN NUMBER) IS
        v_winner VARCHAR2(100);
        v_score NUMBER;
        v_game_status VARCHAR2(20);
    BEGIN
        -- Проверяем, не завершена ли уже игра
        SELECT status INTO v_game_status 
        FROM register.games 
        WHERE game_id = end_game.game_id;
        
        IF v_game_status = 'finished' THEN
            RETURN;
        END IF;
        
        -- Определяем победителя (игрока с максимальным счетом)
        BEGIN
            SELECT player_username, score INTO v_winner, v_score
            FROM register.player_states
            WHERE game_id = end_game.game_id
            ORDER BY score DESC
            FETCH FIRST 1 ROWS ONLY;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN -- Если нет игроков с очками
                v_winner := 'Не определен';
                v_score := 0;
        END;
        
        -- Обновляем таблицу лидеров
        BEGIN
            MERGE INTO register.leaderboard l
            USING (
                SELECT v_winner AS username, v_score AS score FROM dual
            ) s
            ON (l.username = s.username)
            WHEN MATCHED THEN
                UPDATE SET l.score = l.score + s.score
            WHEN NOT MATCHED THEN
                INSERT (username, score)
                VALUES (s.username, s.score);
        EXCEPTION
            WHEN OTHERS THEN NULL;
        END;
        
        -- Обновляем статус игры
        UPDATE register.games
        SET status = 'finished',
            end_time = CURRENT_TIMESTAMP,
            winner = v_winner,
            need_end_game = 0
        WHERE game_id = end_game.game_id;
        
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            NULL;
    END end_game;
END game_timer_pkg;














CREATE OR REPLACE PROCEDURE register.submit_word_and_pass_turn(
    p_game_id IN NUMBER,
    p_username IN VARCHAR2,
    p_word IN VARCHAR2
) IS
    v_current_player VARCHAR2(100);
BEGIN
    -- Проверяем, что это текущий игрок
    SELECT current_player INTO v_current_player
    FROM register.games
    WHERE game_id = p_game_id;
    
    IF v_current_player != p_username THEN
        RAISE_APPLICATION_ERROR(-20001, 'Не ваш ход!');
    END IF;
    
    -- Вставляем слово
    INSERT INTO register.game_moves 
    (game_id, player_username, word, is_valid, move_time)
    VALUES (p_game_id, p_username, p_word, 1, CURRENT_TIMESTAMP);
    
    -- Обновляем счет
    UPDATE register.player_states
    SET score = score + LENGTH(p_word)
    WHERE game_id = p_game_id AND player_username = p_username;
    
    -- Передаем ход следующему игроку
    game_timer_pkg.pass_turn(p_game_id);
    
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END submit_word_and_pass_turn;








CREATE OR REPLACE PROCEDURE register.skip_turn(
    p_game_id IN NUMBER,
    p_username IN VARCHAR2
) IS
    v_current_player VARCHAR2(100);
    v_should_end NUMBER;
BEGIN
    -- Проверяем, что это текущий игрок
    SELECT current_player INTO v_current_player
    FROM register.games
    WHERE game_id = p_game_id;
    
    IF v_current_player != p_username THEN
        RAISE_APPLICATION_ERROR(-20001, 'Не ваш ход!');
    END IF;
    
    -- Добавляем запись о пропуске хода
    INSERT INTO register.game_moves 
    (game_id, player_username, word, is_valid, move_time)
    VALUES (p_game_id, p_username, '[Пропуск хода]', 0, CURRENT_TIMESTAMP);
    
    -- Проверяем условия завершения игры
    v_should_end := game_timer_pkg.should_end_game(p_game_id);
    IF v_should_end = 1 THEN
        game_timer_pkg.end_game(p_game_id);
    ELSE
        -- Передаем ход следующему игроку
        game_timer_pkg.pass_turn(p_game_id);
    END IF;
    
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END skip_turn;








SELECT *  FROM register.games 
WHERE game_id = 333;




ALTER PACKAGE register.game_timer_pkg COMPILE BODY;


SELECT * FROM big_words;

CREATE TABLE big_words (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  word VARCHAR2(100 CHAR)
);

SELECT * FROM small_words;

CREATE TABLE small_words (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  word VARCHAR2(100 CHAR)
);

SELECT * FROM game_moves;
DROP TABLE game_moves;
CREATE TABLE game_moves (
    move_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    game_id NUMBER REFERENCES games(game_id),
    player_username VARCHAR2(50) NOT NULL,
    word VARCHAR2(50) NOT NULL,
    move_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_valid NUMBER(1) DEFAULT 0
);



CREATE TABLE register.game_notifications (
    game_id NUMBER,
    player_username VARCHAR2(100),
    notified NUMBER(1) DEFAULT 0
);


CREATE TABLE games (
    game_id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    owner_username VARCHAR2(50 CHAR) NOT NULL,  -- Владелец игры
    room_name VARCHAR2(50 CHAR) NOT NULL UNIQUE,
    max_players NUMBER(1) CHECK (max_players BETWEEN 2 AND 4),
    password_hash VARCHAR2(128),  -- NULL если без пароля
    current_players NUMBER(1) DEFAULT 0,
    created_by VARCHAR2(50 CHAR),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    turn_time_minutes NUMBER(1) CHECK (turn_time_minutes BETWEEN 1 AND 5),
    is_vs_bot NUMBER(1) DEFAULT 0,
    status VARCHAR2(20 CHAR) DEFAULT 'waiting'  -- Статус игры
);


CREATE TABLE leaderboard (
    username VARCHAR2(50) PRIMARY KEY,
    score NUMBER DEFAULT 0
);


CREATE TABLE players (
    player_id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    game_id NUMBER,
    player_username VARCHAR2(50 CHAR),
    status VARCHAR2(20 CHAR) DEFAULT 'waiting',  -- Статус игрока: ожидает, играет
    score NUMBER DEFAULT 0,  -- Очки игрока
    move_order NUMBER,  -- Порядок хода
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);


CREATE TABLE player_states (
    game_id NUMBER REFERENCES games(game_id),
    player_username VARCHAR2(50) NOT NULL,
    score NUMBER DEFAULT 0,
    is_active NUMBER(1) DEFAULT 1,
    PRIMARY KEY (game_id, player_username)
);


CREATE TABLE USERS (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    username VARCHAR2(50) UNIQUE NOT NULL,
    password VARCHAR2(255) NOT NULL
);
