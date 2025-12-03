import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Movie Explorer",
  description: "A clean landing page ready to connect to your TMDb-powered project.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
