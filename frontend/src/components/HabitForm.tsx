import {Save, X} from "lucide-react";
import {useEffect, useState, type FormEvent} from "react";

import type {Habit, HabitInput, HabitPriority} from "../types";


type HabitFormProps = {
  habit: Habit | null;
  isSaving: boolean;
  onCancel: () => void;
  onSave: (input: HabitInput) => Promise<void>;
};

export function HabitForm({habit, isSaving, onCancel, onSave}: HabitFormProps) {
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<HabitPriority>("medium");

  useEffect(() => {
    setTitle(habit?.title ?? "");
    setCategory(habit?.category ?? "");
    setDescription(habit?.description ?? "");
    setPriority(habit?.priority ?? "medium");
  }, [habit]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    await onSave({
      title: title.trim(),
      category: category.trim() || null,
      description: description.trim() || null,
      priority,
    });
  };

  return (
    <section className="habit-editor" aria-labelledby="habit-editor-title">
      <div className="section-heading">
        <div>
          <p className="section-label">Habit editor</p>
          <h2 id="habit-editor-title">{habit ? "編輯習慣" : "新增習慣"}</h2>
        </div>
        <button type="button" className="icon-button" onClick={onCancel} aria-label="關閉表單" title="關閉">
          <X aria-hidden="true" />
        </button>
      </div>
      <form className="habit-form" onSubmit={submit}>
        <label className="field">
          <span>習慣名稱</span>
          <input value={title} onChange={(event) => setTitle(event.target.value)} maxLength={120} required />
        </label>
        <label className="field">
          <span>分類</span>
          <input value={category} onChange={(event) => setCategory(event.target.value)} maxLength={40} />
        </label>
        <label className="field">
          <span>優先級</span>
          <select
            value={priority}
            onChange={(event) => setPriority(event.target.value as HabitPriority)}
          >
            <option value="high">高</option>
            <option value="medium">中</option>
            <option value="low">低</option>
          </select>
        </label>
        <label className="field field-wide">
          <span>描述</span>
          <textarea value={description} onChange={(event) => setDescription(event.target.value)} maxLength={500} rows={3} />
        </label>
        <div className="form-actions field-wide">
          <button type="button" className="text-button" onClick={onCancel}>取消</button>
          <button type="submit" className="primary-button stable-button" disabled={isSaving || !title.trim()}>
            <Save aria-hidden="true" />
            <span>{isSaving ? "儲存中..." : "儲存習慣"}</span>
          </button>
        </div>
      </form>
    </section>
  );
}
