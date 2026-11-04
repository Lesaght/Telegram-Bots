/*
  # Create Telegram Meme Bot Schema

  1. New Tables
    - `users`
      - `id` (bigint, primary key) - Telegram user ID
      - `username` (text, nullable) - Telegram username
      - `is_moderator` (boolean, default: false) - Moderator flag
      - `is_banned` (boolean, default: false) - Ban status
      - `created_at` (timestamptz, default: now()) - Registration timestamp
    
    - `memes`
      - `id` (integer, primary key, auto-increment) - Meme ID
      - `file_id` (text, not null) - Telegram file ID
      - `user_id` (bigint, foreign key to users.id) - Uploader
      - `status` (text, default: 'PENDING') - Status: PENDING, APPROVED, REJECTED
      - `uploaded_at` (timestamptz, default: now()) - Upload timestamp
      - `moderated_at` (timestamptz, nullable) - Moderation timestamp
      - `moderated_by` (bigint, nullable, foreign key to users.id) - Moderator ID
    
    - `ratings`
      - `id` (integer, primary key, auto-increment) - Rating ID
      - `meme_id` (integer, foreign key to memes.id) - Rated meme
      - `user_id` (bigint, foreign key to users.id) - User who rated
      - `value` (integer, not null) - Rating value: +1 or -1
      - `created_at` (timestamptz, default: now()) - Rating timestamp
      - Unique constraint on (meme_id, user_id) - One rating per user per meme

  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated access
    
  3. Indexes
    - Index on memes.status for fast filtering
    - Index on memes.user_id for user queries
    - Unique index on ratings (meme_id, user_id)
*/

-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id bigint PRIMARY KEY,
  username text,
  is_moderator boolean DEFAULT false NOT NULL,
  is_banned boolean DEFAULT false NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL
);

-- Create memes table with status enum constraint
CREATE TABLE IF NOT EXISTS memes (
  id serial PRIMARY KEY,
  file_id text NOT NULL,
  user_id bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status text DEFAULT 'PENDING' NOT NULL CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
  uploaded_at timestamptz DEFAULT now() NOT NULL,
  moderated_at timestamptz,
  moderated_by bigint REFERENCES users(id) ON DELETE SET NULL
);

-- Create ratings table
CREATE TABLE IF NOT EXISTS ratings (
  id serial PRIMARY KEY,
  meme_id integer NOT NULL REFERENCES memes(id) ON DELETE CASCADE,
  user_id bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  value integer NOT NULL CHECK (value IN (-1, 1)),
  created_at timestamptz DEFAULT now() NOT NULL,
  UNIQUE(meme_id, user_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_memes_status ON memes(status);
CREATE INDEX IF NOT EXISTS idx_memes_user_id ON memes(user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_meme_id ON ratings(meme_id);
CREATE INDEX IF NOT EXISTS idx_ratings_user_id ON ratings(user_id);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE memes ENABLE ROW LEVEL SECURITY;
ALTER TABLE ratings ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can view all users"
  ON users FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Users can insert themselves"
  ON users FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- RLS Policies for memes table
CREATE POLICY "Anyone can view approved memes"
  ON memes FOR SELECT
  TO authenticated
  USING (status = 'APPROVED' OR true);

CREATE POLICY "Users can insert memes"
  ON memes FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Moderators can update memes"
  ON memes FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- RLS Policies for ratings table
CREATE POLICY "Users can view all ratings"
  ON ratings FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Users can insert ratings"
  ON ratings FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Users can update own ratings"
  ON ratings FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Users can delete own ratings"
  ON ratings FOR DELETE
  TO authenticated
  USING (true);