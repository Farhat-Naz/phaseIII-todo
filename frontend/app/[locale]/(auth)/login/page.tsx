import { Metadata } from 'next';
import Link from 'next/link';
import { getTranslations } from 'next-intl/server';
import { LoginForm } from '@/components/features/auth/LoginForm';
import { Card } from '@/components/ui/Card';
import { LanguageSwitcher } from '@/components/features/shared/LanguageSwitcher';

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  // Await params in Next.js 15+
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'auth' });

  return {
    title: `${t('login')} | TodoApp`,
    description: t('login'),
  };
}

export default async function LoginPage({ params }: { params: Promise<{ locale: string }> }) {
  // Await params in Next.js 15+
  const { locale } = await params;

  return (
    <div className={`min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-12 px-4 sm:px-6 lg:px-8 ${locale === 'ur' ? 'font-urdu' : ''}`}>
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <Link href={`/${locale}`}>
            <h1 className="text-4xl font-bold text-primary-600 dark:text-primary-400 mb-2">
              TodoApp
            </h1>
          </Link>
          <div className="flex justify-center items-center gap-3 mt-4">
            <Link
              href={`/${locale}`}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              Home
            </Link>
            <LanguageSwitcher />
          </div>
        </div>

        {/* Login Card */}
        <Card variant="elevated" padding="lg">
          <LoginForm locale={locale} />
        </Card>
      </div>
    </div>
  );
}
