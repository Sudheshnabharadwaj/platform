import React, { useState, useRef } from 'react';
import { User, ShieldCheck, Building2, Camera, Upload, Trash2 } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const ProfilePage: React.FC = () => {
  const [avatarUrl, setAvatarUrl] = useState<string>(
    localStorage.getItem('admin_profile_avatar') || ''
  );
  const [showImageModal, setShowImageModal] = useState(false);
  const [imageUrlInput, setImageUrlInput] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const result = reader.result as string;
        setAvatarUrl(result);
        localStorage.setItem('admin_profile_avatar', result);
        setShowImageModal(false);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSaveUrl = (e: React.FormEvent) => {
    e.preventDefault();
    if (!imageUrlInput.trim()) return;
    setAvatarUrl(imageUrlInput.trim());
    localStorage.setItem('admin_profile_avatar', imageUrlInput.trim());
    setImageUrlInput('');
    setShowImageModal(false);
  };

  const handleRemoveImage = () => {
    setAvatarUrl('');
    localStorage.removeItem('admin_profile_avatar');
    setShowImageModal(false);
  };

  return (
    <div className="space-y-6 font-sans">
      {/* Page Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">My Profile</h1>
        <p className="text-xs text-slate-500 mt-1">
          View your administrative profile and department information.
        </p>
      </div>

      {/* Main Profile Card - Clean theme, no dark strip, image support */}
      <div className="max-w-2xl bg-white border border-slate-200/80 rounded-2xl p-6 sm:p-8 shadow-2xs space-y-6">
        {/* User Identity Header with Profile Avatar Support */}
        <div className="flex items-center justify-between pb-6 border-b border-slate-100 flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="relative group shrink-0">
              {avatarUrl ? (
                <img
                  src={avatarUrl}
                  alt="Hyma"
                  className="w-16 h-16 rounded-2xl object-cover border-2 border-slate-200 shadow-2xs"
                />
              ) : (
                <div className="w-16 h-16 rounded-2xl bg-[#0284C7] text-white flex items-center justify-center font-bold text-xl shadow-xs shrink-0">
                  H
                </div>
              )}

              <button
                type="button"
                onClick={() => setShowImageModal(true)}
                className="absolute -bottom-1 -right-1 p-1.5 rounded-full bg-white border border-slate-200 text-slate-700 hover:text-[#0284C7] hover:border-[#0284C7] shadow-xs cursor-pointer transition-all"
                title="Change profile image"
              >
                <Camera className="w-3.5 h-3.5" />
              </button>
            </div>

            <div>
              <h2 className="text-lg font-bold text-slate-900">Hyma</h2>
              <div className="flex items-center gap-2 mt-1">
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-sky-50 text-[#0284C7] border border-sky-200/60 uppercase">
                  <ShieldCheck className="w-3.5 h-3.5 inline" /> Admin
                </span>
              </div>
            </div>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowImageModal(true)}
            className="border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-semibold"
          >
            <Camera className="w-3.5 h-3.5 mr-1.5 text-[#0284C7]" />
            Change Image
          </Button>
        </div>

        {/* Profile Attributes List - Name, Role, Department */}
        <div className="space-y-3.5">
          <div className="flex items-center justify-between py-3 px-4 rounded-xl bg-slate-50/70 border border-slate-100">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-white text-[#0284C7] border border-slate-200/60">
                <User className="w-4 h-4" />
              </div>
              <span className="text-xs font-semibold text-slate-500">Name</span>
            </div>
            <span className="text-sm font-bold text-slate-900">Hyma</span>
          </div>

          <div className="flex items-center justify-between py-3 px-4 rounded-xl bg-slate-50/70 border border-slate-100">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-white text-[#0284C7] border border-slate-200/60">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <span className="text-xs font-semibold text-slate-500">Role</span>
            </div>
            <span className="text-sm font-bold text-slate-900">Admin</span>
          </div>

          <div className="flex items-center justify-between py-3 px-4 rounded-xl bg-slate-50/70 border border-slate-100">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-white text-[#0284C7] border border-slate-200/60">
                <Building2 className="w-4 h-4" />
              </div>
              <span className="text-xs font-semibold text-slate-500">Department</span>
            </div>
            <span className="text-sm font-bold text-slate-900">IT Support</span>
          </div>
        </div>
      </div>

      {/* Change Profile Image Modal */}
      {showImageModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-md w-full p-6 font-sans">
            <h3 className="text-base font-bold text-slate-900 mb-1">Update Profile Image</h3>
            <p className="text-xs text-slate-500 mb-4">
              Upload a photo from your computer or enter an image URL.
            </p>

            <div className="space-y-4">
              {/* File Upload Option */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Upload Local Image File
                </label>
                <input
                  type="file"
                  ref={fileInputRef}
                  accept="image/*"
                  onChange={handleImageFileChange}
                  className="hidden"
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full border-dashed border-2 border-slate-300 hover:border-[#0284C7] text-slate-700 py-3 font-semibold"
                >
                  <Upload className="w-4 h-4 mr-2 text-[#0284C7]" />
                  Select Image File
                </Button>
              </div>

              <div className="flex items-center gap-3 my-2">
                <div className="h-px bg-slate-200 flex-1" />
                <span className="text-[10px] font-bold text-slate-400 uppercase">OR</span>
                <div className="h-px bg-slate-200 flex-1" />
              </div>

              {/* URL Input Option */}
              <form onSubmit={handleSaveUrl} className="space-y-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">
                    Paste Image URL
                  </label>
                  <input
                    type="url"
                    placeholder="https://example.com/avatar.jpg"
                    value={imageUrlInput}
                    onChange={(e) => setImageUrlInput(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-[#0284C7]"
                  />
                </div>

                <div className="flex items-center justify-between pt-2">
                  {avatarUrl ? (
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={handleRemoveImage}
                      className="text-red-600 hover:bg-red-50 text-xs font-semibold"
                    >
                      <Trash2 className="w-3.5 h-3.5 mr-1" /> Remove Image
                    </Button>
                  ) : <div />}

                  <div className="flex items-center gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setShowImageModal(false)}
                      className="border-slate-200 text-slate-600"
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      variant="primary"
                      disabled={!imageUrlInput.trim()}
                      className="bg-[#0284C7] text-white"
                    >
                      Save Image URL
                    </Button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
