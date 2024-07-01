import hashlib
import streamlit as st

# Helper function for password encryption
def encrypt_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = encrypt_password(password)
        self.bookings = []

    def add_booking(self, booking):
        self.bookings.append(booking)

    def cancel_booking(self, booking_index):
        if 0 <= booking_index < len(self.bookings):
            cancelled_booking = self.bookings.pop(booking_index)
            return f"Cancelled booking: {cancelled_booking.hotel.name} for {cancelled_booking.number_of_nights} nights."
        else:
            return "Invalid booking index."

class Hotel:
    def __init__(self, name, location, price_per_night, rooms_available):
        self.name = name
        self.location = location
        self.price_per_night = price_per_night
        self.rooms_available = rooms_available

class Booking:
    def __init__(self, user, hotel, number_of_nights, number_of_rooms):
        self.user = user
        self.hotel = hotel
        self.number_of_nights = number_of_nights
        self.number_of_rooms = number_of_rooms
        self.total_price = hotel.price_per_night * number_of_nights * number_of_rooms
        hotel.rooms_available -= number_of_rooms

class HotelBookingSystem:
    def __init__(self):
        self.users = []
        self.hotels = [
            Hotel("Hotel California", "Los Angeles", 200, 10),
            Hotel("The Grand Budapest", "Zubrowka", 300, 5),
            Hotel("The Plaza", "New York", 400, 8),
            Hotel("Marina Bay Sands", "Singapore", 500, 12)
        ]

    def register_user(self, username, password):
        if self.find_user(username):
            return f"User {username} already exists."
        else:
            new_user = User(username, password)
            self.users.append(new_user)
            return f"User {username} registered successfully."

    def login_user(self, username, password):
        user = self.find_user(username)
        if user and user.password == encrypt_password(password):
            return user
        else:
            return None

    def find_user(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return None

    def show_hotels(self):
        hotels_info = []
        for i, hotel in enumerate(self.hotels, 1):
            hotels_info.append(f"{i}. {hotel.name} in {hotel.location} - ${hotel.price_per_night} per night - {hotel.rooms_available} rooms available")
        return hotels_info

    def book_hotel(self, user, hotel_index, number_of_nights, number_of_rooms):
        if 0 < hotel_index <= len(self.hotels):
            hotel = self.hotels[hotel_index - 1]
            if hotel.rooms_available >= number_of_rooms:
                new_booking = Booking(user, hotel, number_of_nights, number_of_rooms)
                user.add_booking(new_booking)
                return f"Booking successful: {hotel.name} for {number_of_nights} nights and {number_of_rooms} rooms. Total price: ${new_booking.total_price}"
            else:
                return f"Not enough rooms available. Only {hotel.rooms_available} rooms left."
        else:
            return "Invalid hotel choice."

    def view_bookings(self, user):
        if user.bookings:
            bookings_info = []
            for i, booking in enumerate(user.bookings, 1):
                bookings_info.append(f"{i}. {booking.hotel.name} for {booking.number_of_nights} nights and {booking.number_of_rooms} rooms. Total price: ${booking.total_price}")
            return bookings_info
        else:
            return ["No bookings found."]

    def cancel_booking(self, user, booking_index):
        if 0 <= booking_index - 1 < len(user.bookings):
            cancelled_booking = user.bookings.pop(booking_index - 1)
            cancelled_booking.hotel.rooms_available += cancelled_booking.number_of_rooms
            return f"Cancelled booking: {cancelled_booking.hotel.name} for {cancelled_booking.number_of_nights} nights and {cancelled_booking.number_of_rooms} rooms."
        else:
            return "Invalid booking index."

    def update_profile(self, user, new_username, new_password):
        user.username = new_username
        user.password = encrypt_password(new_password)
        return f"Profile updated: Username - {new_username}"

def main():
    system = HotelBookingSystem()
    st.title("Hotel Booking System")

    menu = ["Register", "Login", "Show Hotels", "Book Hotel", "View Bookings", "Cancel Booking", "Update Profile"]
    choice = st.sidebar.selectbox("Menu", menu)

    if "user" not in st.session_state:
        st.session_state.user = None

    if choice == "Register":
        st.subheader("Register")
        username= st.text_input("Enter username")
        password = st.text_input("Enter password", type="password")
        if st.button("Register"):
            message = system.register_user(username, password)
            st.success(message)
            st.write(username)
            st.write(password)

    elif choice == "Login":
        st.subheader("Login")
        username = st.text_input("Enter username")
        password = st.text_input("Enter password", type="password")
        if st.button("Login"):
            user = system.login_user(username, password)
            if user:
                st.session_state.user = user
                st.success(f"User {username} logged in successfully.")
            else:
                st.error("Invalid username or password.")

    elif choice == "Show Hotels":
        st.subheader("Available Hotels")
        hotels = system.show_hotels()
        for hotel in hotels:
            st.text(hotel)

    elif choice == "Book Hotel":
        if st.session_state.user:
            st.subheader("Book Hotel")
            hotels = system.show_hotels()
            for hotel in hotels:
                st.text(hotel)
            hotel_index = st.number_input("Choose a hotel (number)", min_value=1, max_value=len(system.hotels))
            number_of_nights = st.number_input("Enter number of nights", min_value=1)
            number_of_rooms = st.number_input("Enter number of rooms", min_value=1)
            if st.button("Book"):
                message = system.book_hotel(st.session_state.user, hotel_index, number_of_nights, number_of_rooms)
                st.success(message)
        else:
            st.warning("You need to login first.")

    elif choice == "View Bookings":
        if st.session_state.user:
            st.subheader("Your Bookings")
            bookings = system.view_bookings(st.session_state.user)
            for booking in bookings:
                st.text(booking)
        else:
            st.warning("You need to login first.")

    elif choice == "Cancel Booking":
        if st.session_state.user:
            st.subheader("Cancel Booking")
            bookings = system.view_bookings(st.session_state.user)
            for booking in bookings:
                st.text(booking)
            booking_index = st.number_input("Enter booking number to cancel", min_value=1)
            if st.button("Cancel"):
                message = system.cancel_booking(st.session_state.user, booking_index)
                st.success(message)
        else:
            st.warning("You need to login first.")

    elif choice == "Update Profile":
        if st.session_state.user:
            st.subheader("Update Profile")
            new_username = st.text_input("Enter new username")
            new_password = st.text_input("Enter new password", type="password")
            if st.button("Update"):
                message = system.update_profile(st.session_state.user, new_username, new_password)
                st.success(message)
        else:
            st.warning("You need to login first.")

if __name__ == "__main__":
    main()
