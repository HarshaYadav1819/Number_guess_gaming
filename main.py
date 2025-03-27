import streamlit as st
import pandas as pd
import random
import time
from supabase import create_client

# This must be the VERY FIRST Streamlit command
st.set_page_config(page_title="Number Guessing Game", page_icon="🎲")

class SupabaseManager:
    def __init__(self):
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            self.supabase = create_client(url, key)
        except Exception as e:
            st.error(f"Supabase connection error: {e}")
    
    def save_high_score(self, difficulty, attempts, time_taken, player_name):
        """Save high score to Supabase"""
        try:
            data = {
                "difficulty": difficulty,
                "attempts": attempts,
                "time_taken": time_taken,
                "player_name": player_name
            }
            
            response = self.supabase.table("high_scores").insert(data).execute()
            return response
        except Exception as e:
            st.error(f"Error saving high score: {e}")
            return None
    
    def get_high_scores(self, difficulty=None):
        """Retrieve high scores from Supabase"""
        try:
            if difficulty:
                response = (self.supabase.table("high_scores")
                          .select("*")
                          .eq("difficulty", difficulty)
                          .order("attempts")
                          .limit(10)
                          .execute())
            else:
                response = (self.supabase.table("high_scores")
                          .select("*")
                          .order("attempts")
                          .limit(10)
                          .execute())
            
            return response.data
        except Exception as e:
            st.error(f"Error retrieving high scores: {e}")
            return []

def main():
    # Initialize Supabase manager
    db_manager = SupabaseManager()
    
    st.title("🎲 Number Guessing Game")
    
    # Initialize game state
    if 'target_number' not in st.session_state:
        st.session_state.target_number = random.randint(1, 100)
        st.session_state.attempts = 0
        st.session_state.game_over = False
        st.session_state.start_time = time.time()
    
    # Difficulty selection
    difficulty = st.selectbox(
        "Select Difficulty",
        ["Easy (10 attempts)", "Medium (5 attempts)", "Hard (3 attempts)"]
    )
    
    max_attempts = {
        "Easy (10 attempts)": 10,
        "Medium (5 attempts)": 5,
        "Hard (3 attempts)": 3
    }[difficulty]
    
    # Player name input
    player_name = st.text_input("Enter Your Name")
    
    # Guess input
    guess = st.number_input(
        "Guess a number between 1 and 100", 
        min_value=1, 
        max_value=100
    )
    
    # Submit guess button
    if st.button("Submit Guess"):
        if not player_name:
            st.warning("Please enter your name!")
            return
        
        st.session_state.attempts += 1
        
        if guess == st.session_state.target_number:
            st.balloons()
            st.success(f"Congratulations! You guessed the number in {st.session_state.attempts} attempts!")
            
            # Save high score
            time_taken = time.time() - st.session_state.start_time
            db_manager.save_high_score(
                difficulty, 
                st.session_state.attempts, 
                time_taken, 
                player_name
            )
            
            st.session_state.game_over = True
        
        elif guess < st.session_state.target_number:
            st.info("Too low! Guess higher.")
        else:
            st.info("Too high! Guess lower.")
        
        if st.session_state.attempts >= max_attempts and not st.session_state.game_over:
            st.error(f"Game Over! The number was {st.session_state.target_number}")
            st.session_state.game_over = True
    
    # High Scores Section
    st.header("🏆 High Scores")
    high_scores = db_manager.get_high_scores(difficulty)
    
    if high_scores:
        high_score_df = pd.DataFrame(high_scores)
        st.dataframe(high_score_df[['player_name', 'attempts', 'time_taken', 'created_at']])
    else:
        st.write("No high scores yet!")
    
    # New Game Button
    if st.button("Start New Game"):
        st.session_state.target_number = random.randint(1, 100)
        st.session_state.attempts = 0
        st.session_state.game_over = False
        st.session_state.start_time = time.time()

if __name__ == "__main__":
    main()