import "./globals.css";

export const metadata = {
  title: "Ayurvedic Chatbot",
  description: "AI-based Ayurveda Recommendation System",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
