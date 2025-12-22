'use client';

import { useEffect, useState } from 'react';

export default function Home() {
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMessage = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL;
        if (!apiUrl) {
          throw new Error('NEXT_PUBLIC_API_URL is not defined');
        }
        const response = await fetch(apiUrl);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setMessage(data.message);
      } catch (e: any) {
        setError(`Failed to fetch message: ${e.message}`);
      }
    };

    fetchMessage();
  }, []);

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-center py-32 px-16 bg-white dark:bg-black sm:items-start">
        <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
          <h1 className="max-w-xs text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50">
            Message from the API:
          </h1>
          {error ? (
            <p className="max-w-md text-lg leading-8 text-red-600 dark:text-red-400">
              {error}
            </p>
          ) : (
            <p className="max-w-md text-lg leading-8 text-zinc-600 dark:text-zinc-400">
              {message || 'Loading...'}
            </p>
          )}
        </div>
      </main>
    </div>
  );
}
