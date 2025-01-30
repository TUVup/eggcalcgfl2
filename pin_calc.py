import tkinter as tk
from tkinter import messagebox
from itertools import combinations
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class VoucherCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("에그머니 소망 패키지 계산기")
        self.package_list = []
        
        # 입력 프레임
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10)
        
        # 안내 레이블 추가
        # 안내 레이블을 맨 위에 배치
        guide_label = tk.Label(root, text="패키지 가격은 할인 전 원가로 넣어주세요")
        guide_label.pack(pady=5)
        self.amount_entry = tk.Entry(input_frame)
        self.amount_entry.insert(0, "할인 전 원가로 넣어주세요")
        self.amount_entry.bind("<FocusIn>", lambda e: self.amount_entry.delete(0, tk.END))
        self.amount_entry.pack(side=tk.LEFT, padx=5)
        
        add_button = tk.Button(input_frame, text="패키지 금액 추가", command=self.add_amount)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # 리스트 표시 영역
        self.list_frame = tk.Frame(root)
        self.list_frame.pack(pady=10)
        
        self.amount_listbox = tk.Listbox(self.list_frame, width=40, height=10)
        self.amount_listbox.pack(side=tk.LEFT)
        
        # 스크롤바
        scrollbar = tk.Scrollbar(self.list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.amount_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.amount_listbox.yview)
        
        # 버튼 프레임
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        calculate_button = tk.Button(button_frame, text="계산하기", command=self.calculate)
        calculate_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = tk.Button(button_frame, text="선택 항목 지우기", command=self.delete_selected)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = tk.Button(button_frame, text="목록 전체 지우기", command=self.clear_list)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # 결과 표시 영역
        self.result_text = tk.Text(root, width=40, height=10)
        self.result_text.pack(pady=10)
        
        # 시뮬레이션 버튼을 별도의 프레임으로 생성하여 맨 아래에 배치
        simulation_frame = tk.Frame(root)
        simulation_frame.pack(pady=10)
        
        simulation_button = tk.Button(simulation_frame, text="핀 사용 시뮬레이션", command=self.show_simulation)
        simulation_button.pack()
        
        # 시뮬레이션 창 초기화
        self.simulation_window = None
        self.simulate_text = None

    def add_amount(self):
        try:
            amount = int(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("오류", "0보다 큰 금액을 입력하세요.")
                return
            if amount > 250000:
                messagebox.showerror("오류", "250,000원 이하의 금액을 입력하세요.")
                return
            
            discount = amount * 0.95
            self.package_list.append(int(discount))
            self.amount_listbox.insert(tk.END, f"{int(discount):,}원(할인 전 {amount:,}원)")
            self.amount_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("오류", "올바른 금액을 입력하세요.")

    def delete_selected(self):
        try:
            # 선택된 인덱스 가져오기
            selected_indices = self.amount_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("경고", "삭제할 항목을 선택하세요.")
                return
            
            # 큰 인덱스부터 삭제 (작은 인덱스부터 삭제하면 인덱스가 변경됨)
            for index in sorted(selected_indices, reverse=True):
                del self.package_list[index]
                self.amount_listbox.delete(index)
                
            # 결과 텍스트 초기화
            self.result_text.delete(1.0, tk.END)
            
        except Exception as e:
            messagebox.showerror("오류", f"삭제 중 오류가 발생했습니다: {str(e)}")

    def clear_list(self):
        self.package_list.clear()
        self.amount_listbox.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.simulate_text.delete(1.0, tk.END)

    def find_pins_for_amount(self, voucher_list, package_list):
        self.simulate_text.insert(tk.END, f"사용될 핀: {voucher_list}\n\n")
        total_package = sum(package_list)
        self.result = False
        sorted_pins = sorted(voucher_list)
        print(f"first insert sorted_pins: {sorted_pins}")

        for package in package_list:
            print(f"package: {package}, package_list: {package_list}, sorted_pins: {sorted_pins}")
            self.result = False
            selected_pins = []
            total_selected = 0
            best_combination = []
            best_total = 0

            for balance in sorted_pins:
                if total_selected >= package:
                    break
                selected_pins.append(balance)
                total_selected += balance

            if total_selected >= package and len(selected_pins) <= 5:
                # 사용된 핀들 제거하고 잔액 처리
                remaining = total_selected - package
                
                # 사용된 핀들을 sorted_pins에서 제거
                for pin in selected_pins:
                    sorted_pins.remove(pin)
                
                # 잔액이 있다면 sorted_pins에 추가
                if remaining > 0:
                    sorted_pins.append(remaining)
                    sorted_pins.sort()  # 다시 정렬
                
                total_package -= package
                print(f"smallest sorted_pins: {sorted_pins}")
                self.simulate_text.insert(tk.END, f"---{package:,}원 결제---\n사용된 핀: {len(selected_pins)}개\n") # 핀 사용 금액: {total_selected:,}원\n
                if sorted_pins != []:
                    self.simulate_text.insert(tk.END, f"사용 후 남은 잔액: {sorted_pins}원\n")
                else:
                    self.simulate_text.insert(tk.END, "사용 후 남은 잔액: 0원\n")  

                self.result = True
                # break
            else:
                # 가능한 모든 조합을 고려하여 최적의 조합을 찾음
                for r in range(1, 6):
                    for combination in combinations(sorted_pins, r):
                        total = sum(balance for balance in combination)
                        if total >= package and (best_total == 0 or total < best_total):
                            best_combination = combination
                            best_total = total

                if best_total >= package:
                    # 사용된 핀들 제거하고 잔액 처리
                    remaining = best_total - package
                    used_pins = list(best_combination)
                    
                    # 사용된 핀들을 sorted_pins에서 제거
                    for pin in used_pins:
                        sorted_pins.remove(pin)
                    
                    # 잔액이 있다면 sorted_pins에 추가
                    if remaining > 0:
                        sorted_pins.append(remaining)
                        sorted_pins.sort()  # 다시 정렬
                    
                    total_package -= package
                    print(f"best_combination sorted_pins: {sorted_pins}")
                    self.simulate_text.insert(tk.END, f"---{package:,}원 결제---\n사용된 핀: {len(used_pins)}개\n") # 핀 사용 금액: {best_total:,}원\n
                    if sorted_pins != []:
                        self.simulate_text.insert(tk.END, f"사용 후 남은 잔액: {sorted_pins}원\n")
                    else:
                        self.simulate_text.insert(tk.END, "사용 후 남은 잔액: 0원\n")

                    self.result = True
                    # break
        
            if not self.result:
                print(f"break: {self.result}")
                self.result_text.insert(tk.END, f"{package:,}원권을 사용할 수 있는 5개 미만의 핀 조합을 찾을 수 없습니다.\n")
                self.simulate_text.insert(tk.END, f"---{package:,}원 결제---\n사용할 수 있는 5개 미만의 핀 조합을 찾을 수 없습니다.\n")
                break
        
        print(f"final selected_pins: {selected_pins}")
        return self.result

    def calculate(self):
        if not self.package_list:
            messagebox.showwarning("경고", "계산할 금액이 없습니다.")
            return
        
        # 시뮬레이션 창 생성
        self.show_simulation()
            
        total_cost = sum(self.package_list)
        available_vouchers = [1000, 3000, 5000, 10000, 30000, 50000]
        best_combination = self._find_best_combination_package(total_cost, available_vouchers)
        print(f"best_combination: {best_combination}")
        
        # 결과 출력
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"패키지 총 구매 금액: {total_cost:,}원\n\n")
        self.result_text.insert(tk.END, "최적의 상품권 조합:\n")
        
        # 상품권별 개수 계산
        voucher_counts = {}
        for voucher in best_combination:
            voucher_counts[voucher] = voucher_counts.get(voucher, 0) + 1

        result = self.find_pins_for_amount(best_combination, sorted(self.package_list))
        print(f"final result: {result}")
        if result:
            print("result: ", result)
        
        # 상품권별 개수 출력
            for voucher, count in sorted(voucher_counts.items()):
                self.result_text.insert(tk.END, f"{voucher:,}원권 x {count}장\n")
            
            # 총 사용 금액 계산
            total_used = sum(best_combination)
            self.result_text.insert(tk.END, f"\n상품권 총 사용 금액: {total_used:,}원\n")
            self.result_text.insert(tk.END, f"잔액: {total_used - total_cost:,}원")
        else:
            for voucher, count in sorted(voucher_counts.items()):
                self.result_text.insert(tk.END, f"{voucher:,}원권 x {count}장\n")            

            total_used = sum(best_combination)
            self.result_text.insert(tk.END, f"\n상품권 총 사용 금액: {total_used:,}원\n")
            self.result_text.insert(tk.END, f"잔액: {total_used - total_cost:,}원")

            self.result_text.insert(tk.END, "!!주의!!\n최소 잔액을 남기는 조합을 찾았으나 5개 미만으로 사용할 수 없습니다.\n참고용으로만 사용해주세요.\n\n")

    def _find_best_combination_package(self, total_amount, available_vouchers):
        # dp[i]는 금액 i를 만들기 위한 최소 잔액을 저장
        dp = [float('inf')] * (total_amount + 50001)  # 최대 권종(50000)만큼 여유 공간 추가
        dp[0] = 0
        
        # 각 금액에 대해 가능한 최소 잔액 계산
        for amount in range(total_amount + 1):
            if dp[amount] == float('inf'):
                continue
            for voucher in available_vouchers:
                next_amount = amount + voucher
                dp[next_amount] = min(dp[next_amount], next_amount - total_amount)
        
        # 목표 금액 이상이면서 최소 잔액을 가진 금액 찾기
        min_remainder = float('inf')
        target_amount = total_amount
        for amount in range(total_amount, total_amount + 50001):
            if dp[amount] != float('inf') and dp[amount] < min_remainder:
                min_remainder = dp[amount]
                target_amount = amount
        
        # 선택된 금액을 만들기 위한 상품권 조합 찾기
        result = []
        remaining = target_amount
        for voucher in sorted(available_vouchers, reverse=True):
            while remaining >= voucher:
                result.append(voucher)
                remaining -= voucher
        
        return result

    def show_simulation(self):
        if not self.package_list:
            messagebox.showwarning("경고", "계산할 금액이 없습니다.")
            return
            
        # 기존 창이 있다면 앞으로 가져오기
        if self.simulation_window is not None:
            try:
                self.simulation_window.lift()
                self.simulation_window.focus_force()
                return
            except tk.TclError:
                pass
        
        # 새 창 생성
        self.simulation_window = tk.Toplevel(self.root)
        self.simulation_window.title("핀 사용 시뮬레이션")
        
        # 새 텍스트 위젯 생성
        self.simulate_text = tk.Text(self.simulation_window, width=40, height=10)
        self.simulate_text.pack(padx=10, pady=10)
        
        # 창 위치 설정
        window_width = self.root.winfo_screenwidth()
        window_height = self.root.winfo_screenheight()
        width = self.simulation_window.winfo_reqwidth()
        height = self.simulation_window.winfo_reqheight()
        x = (window_width - width) // 2
        y = (window_height - height) // 2
        self.simulation_window.geometry(f"+{x}+{y}")
        
        # 시뮬레이션 실행
        total_cost = sum(self.package_list)
        available_vouchers = [1000, 3000, 5000, 10000, 30000, 50000]
        best_combination = self._find_best_combination_package(total_cost, available_vouchers)
        
        # 시뮬레이션 텍스트 초기화
        self.simulate_text.delete(1.0, tk.END)
        self.simulate_text.insert(tk.END, f"패키지 총 구매 금액: {total_cost:,}원\n\n")
        
        # 핀 사용 시뮬레이션 실행
        result = self.find_pins_for_amount(best_combination, sorted(self.package_list))
        
        if not result:
            self.simulate_text.insert(tk.END, "\n!!주의!!\n최소 잔액을 남기는 조합을 찾았으나\n5개 미만으로 사용할 수 없습니다.\n참고용으로만 사용해주세요.")

def main():
    root = tk.Tk()
    root.iconbitmap(resource_path('EggCalc.ico'))

    window_width = root.winfo_screenwidth()
    window_height = root.winfo_screenheight()

    # _ = VoucherCalculator(root)

    # 위젯에 맞게 윈도우 크기 조정
    root.update_idletasks()  # 위젯들의 크기를 계산하기 위해 업데이트
    width = root.winfo_reqwidth()
    height = root.winfo_reqheight()

    x = (window_width - width) // 2
    y = (window_height - height) // 2

    root.geometry(f"+{x}+{y}")

    _ = VoucherCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()