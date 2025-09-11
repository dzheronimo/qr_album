import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Демо | StoryQR',
  description: 'Интерактивная демонстрация возможностей StoryQR',
};

export default function DemoPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Демонстрация StoryQR
          </h1>
          <p className="text-xl text-gray-600">
            Посмотрите, как работает создание QR-альбомов
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Demo Card 1 */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              Создание альбома
            </h3>
            <p className="text-gray-600 mb-4">
              Создайте альбом с QR-кодами для быстрого доступа к контенту
            </p>
            <div className="bg-gray-100 rounded p-4 text-sm text-gray-700">
              <p>1. Нажмите "Создать альбом"</p>
              <p>2. Заполните название и описание</p>
              <p>3. Добавьте страницы с медиафайлами</p>
            </div>
          </div>

          {/* Demo Card 2 */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="w-16 h-16 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              QR-коды
            </h3>
            <p className="text-gray-600 mb-4">
              Генерируйте QR-коды для мгновенного доступа к вашим страницам
            </p>
            <div className="bg-gray-100 rounded p-4 text-sm text-gray-700">
              <p>1. Загрузите медиафайлы</p>
              <p>2. Создайте QR-код</p>
              <p>3. Скачайте и распечатайте</p>
            </div>
          </div>

          {/* Demo Card 3 */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              Поделиться
            </h3>
            <p className="text-gray-600 mb-4">
              Делитесь QR-кодами с друзьями и коллегами
            </p>
            <div className="bg-gray-100 rounded p-4 text-sm text-gray-700">
              <p>1. Скачайте QR-код</p>
              <p>2. Распечатайте или отправьте</p>
              <p>3. Получатели сканируют и получают доступ</p>
            </div>
          </div>

          {/* Demo Card 4 */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="w-16 h-16 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              Аналитика
            </h3>
            <p className="text-gray-600 mb-4">
              Отслеживайте статистику просмотров ваших QR-кодов
            </p>
            <div className="bg-gray-100 rounded p-4 text-sm text-gray-700">
              <p>1. Просматривайте статистику</p>
              <p>2. Анализируйте популярность</p>
              <p>3. Экспортируйте данные</p>
            </div>
          </div>
        </div>

        <div className="text-center mt-12">
          <a
            href="/auth/register"
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            Начать использовать StoryQR
          </a>
        </div>
      </div>
    </div>
  );
}
