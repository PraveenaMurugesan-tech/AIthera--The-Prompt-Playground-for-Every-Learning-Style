import { Outlet } from 'react-router-dom'
import { Footer } from './Footer'
import { Navbar } from './Navbar'
import { ToastContainer } from '../common/ToastContainer'

export const MainLayout = () => {
  return (
    <div className="app-shell">
      <Navbar />
      <div className="content-shell">
        <main className="main-content">
          <Outlet />
        </main>
      </div>
      <Footer />
      <ToastContainer />
    </div>
  )
}
