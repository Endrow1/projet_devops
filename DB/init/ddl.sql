-- ---------------------------------------------------------------------
--  Nettoyage (ordre inverse à cause de la clé étrangère)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS votes;
DROP TABLE IF EXISTS questions;

-- ---------------------------------------------------------------------
--  questions
-- ---------------------------------------------------------------------
CREATE TABLE questions (
                           id          INT UNSIGNED  NOT NULL AUTO_INCREMENT,
                           option_a    VARCHAR(255)  NOT NULL,
                           option_b    VARCHAR(255)  NOT NULL,
                           created_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                           PRIMARY KEY (id)
);

-- ---------------------------------------------------------------------
--  votes
-- ---------------------------------------------------------------------
CREATE TABLE votes (
                       id           INT UNSIGNED  NOT NULL AUTO_INCREMENT,
                       question_id  INT UNSIGNED  NOT NULL,
                       choice       ENUM('A','B') NOT NULL,
                       created_at   TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                       PRIMARY KEY (id),
                       KEY idx_votes_question_id (question_id),
                       CONSTRAINT fk_votes_question
                           FOREIGN KEY (question_id) REFERENCES questions (id)
                               ON DELETE CASCADE
                               ON UPDATE CASCADE
);

-- =====================================================================
--  FIXTURES
-- =====================================================================
-- --- Questions --------------------------------------------------------
INSERT INTO questions (id, option_a, option_b) VALUES
                                                   (1, 'Le sucré',        'Le salé'),
                                                   (2, 'La montagne',     'La mer'),
                                                   (3, 'Le café',         'Le thé'),
                                                   (4, 'Chien',           'Chat'),
                                                   (5, 'Été',             'Hiver'),
                                                   (6, 'Pizza ananas',    'Pizza sans ananas');  -- question sans aucun vote

-- --- Votes ------------------------------------------------------------
INSERT INTO votes (question_id, choice) VALUES
                                            (1,'A'),(1,'A'),(1,'A'),(1,'A'),
                                            (1,'B'),(1,'B'),(1,'B'),(1,'B'),(1,'B'),(1,'B');

INSERT INTO votes (question_id, choice) VALUES
                                            (2,'A'),(2,'A'),(2,'A'),(2,'A'),(2,'A'),(2,'A'),(2,'A'),
                                            (2,'B'),(2,'B'),(2,'B');

INSERT INTO votes (question_id, choice) VALUES
                                            (3,'A'),(3,'A'),(3,'A'),(3,'A'),(3,'A'),
                                            (3,'B'),(3,'B'),(3,'B'),(3,'B'),(3,'B');

INSERT INTO votes (question_id, choice) VALUES
                                            (4,'A'),(4,'A');

INSERT INTO votes (question_id, choice) VALUES
                                            (5,'B'),(5,'B'),(5,'B');

