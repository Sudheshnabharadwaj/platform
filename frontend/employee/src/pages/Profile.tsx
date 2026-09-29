import React, { useState, useEffect, useRef } from 'react';
import { User, Mail, Shield, Building, Phone, BadgeCheck, Camera, Upload, Trash2 } from 'lucide-react';
import { EmployeeService } from '../services/employeeService';
import type { EmployeeProfile } from '../types';
import { Button } from '../components/ui/Button';

export const Profile: React.FC = () => {
  const [profile, setProfile] = useState<EmployeeProfile | null>(null);
  const [showImageModal, setShowImageModal] = useState(false);
  const [imageUrlInput, setImageUrlInput] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setProfile(EmployeeService.getProfile());
  }, []);

  if (!profile) return null;

  const handleImageFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const result = reader.result as string;
        const updated = EmployeeService.updateProfile({ avatarUrl: result });
        setProfile(updated);
        setShowImageModal(false);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSaveUrl = (e: React.FormEvent) => {
    e.preventDefault();
    if (!imageUrlInput.trim()) return;
    const updated = EmployeeService.updateProfile({ avatarUrl: imageUrlInput.trim() });
    setProfile(updated);
    setImageUrlInput('');
    setShowImageModal(false);
  };

  const handleRemoveImage = () => {
    const updated = EmployeeService.updateProfile({ avatarUrl: '' });
    setProfile(updated);
    setShowImageModal(false);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 font-sans pb-12">
      {/* Clean Profile Header Card (No Dark Strip, No Ticket Symbol) */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-2xs p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
        <div className="flex items-center gap-5">
          {/* Avatar Area with Change Image Trigger */}
          <div className="relative group shrink-0">
            {profile.avatarUrl ? (
              <img
                src={profile.avatarUrl}
                alt={profile.name}
                className="w-20 h-20 rounded-2xl object-cover border-2 border-slate-200 shadow-2xs"
              />
            ) : (
              <div className="w-20 h-20 rounded-2xl bg-[#0284C7] text-white flex items-center justify-center font-bold text-2xl shadow-2xs">
                {profile.name
                  .split(' ')
                  .map((n) => n[0])
                  .join('')}
              </div>
            )}

            <button
              type="button"
              onClick={() => setShowImageModal(true)}
              className="absolute -bottom-1.5 -right-1.5 p-1.5 rounded-full bg-white border border-slate-200 text-slate-700 hover:text-[#0284C7] hover:border-[#0284C7] shadow-xs cursor-pointer transition-all"
              title="Change profile image"
            >
              <Camera className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-slate-900">{profile.name}</h1>
              <BadgeCheck className="w-5 h-5 text-[#0284C7]" />
            </div>
            <p className="text-xs font-semibold text-slate-500">{profile.role} • {profile.department}</p>
            <div className="inline-block pt-1">
              <button
                type="button"
                onClick={() => setShowImageModal(true)}
                className="text-xs font-bold text-[#0284C7] hover:underline cursor-pointer"
              >
                Change Profile Image
              </button>
            </div>
          </div>
        </div>

        <div className="bg-sky-50 border border-sky-100 px-4 py-2 rounded-xl text-xs font-mono font-bold text-[#0284C7] shrink-0">
          ID: {profile.employeeId}
        </div>
      </div>

      {/* Main Profile Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Personal Details */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-2xs space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <User className="w-4 h-4 text-[#0284C7]" />
            <h2 className="text-sm font-bold text-slate-900">Employee Information</h2>
          </div>

          <div className="space-y-3.5 pt-1">
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-500 font-medium flex items-center gap-2">
                <User className="w-3.5 h-3.5 text-slate-400" /> Full Name
              </span>
              <span className="text-xs font-bold text-slate-800">{profile.name}</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-500 font-medium flex items-center gap-2">
                <Shield className="w-3.5 h-3.5 text-slate-400" /> Employee ID
              </span>
              <span className="text-xs font-mono font-bold text-[#0284C7]">{profile.employeeId}</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-500 font-medium flex items-center gap-2">
                <Mail className="w-3.5 h-3.5 text-slate-400" /> Email Address
              </span>
              <span className="text-xs font-semibold text-slate-800">{profile.email}</span>
            </div>
          </div>
        </div>

        {/* Organization & Role */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-2xs space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <Building className="w-4 h-4 text-[#0284C7]" />
            <h2 className="text-sm font-bold text-slate-900">Department & Contact</h2>
          </div>

          <div className="space-y-3.5 pt-1">
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-500 font-medium flex items-center gap-2">
                <Building className="w-3.5 h-3.5 text-slate-400" /> Department
              </span>
              <span className="text-xs font-bold text-slate-800">{profile.department}</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-500 font-medium flex items-center gap-2">
                <Shield className="w-3.5 h-3.5 text-slate-400" /> System Role
              </span>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                {profile.role}
              </span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-500 font-medium flex items-center gap-2">
                <Phone className="w-3.5 h-3.5 text-slate-400" /> Contact Number
              </span>
              <span className="text-xs font-semibold text-slate-800">{profile.phone}</span>
            </div>
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
                  {profile.avatarUrl ? (
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
