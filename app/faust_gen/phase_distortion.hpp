/* ------------------------------------------------------------
name: "phase_distortion"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn PhaseDistortion -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __PhaseDistortion_H__
#define  __PhaseDistortion_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS PhaseDistortion
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif


class PhaseDistortion : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec0[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fRec1[2];
	FAUSTFLOAT fHslider1;
	float fConst1;
	int iRec2[2];
	float fConst2;
	float fConst3;
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	FAUSTFLOAT fHslider4;
	float fConst4;
	float fRec3[2];
	FAUSTFLOAT fHslider5;
	
 public:
	PhaseDistortion() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn PhaseDistortion -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "phase_distortion.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "phase_distortion");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 0.4f / std::max<float>(1.0f, 0.3f * fConst0);
		fConst2 = std::max<float>(1.0f, 0.002f * fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.25f);
		fHslider1 = FAUSTFLOAT(0.005f);
		fHslider2 = FAUSTFLOAT(0.14f);
		fHslider3 = FAUSTFLOAT(0.32f);
		fHslider4 = FAUSTFLOAT(2.2e+02f);
		fHslider5 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec3[l5] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual PhaseDistortion* clone() {
		return new PhaseDistortion();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("phase_distortion");
		ui_interface->addHorizontalSlider("attack", &fHslider1, FAUSTFLOAT(0.005f), FAUSTFLOAT(0.001f), FAUSTFLOAT(0.5f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("brighttime", &fHslider2, FAUSTFLOAT(0.14f), FAUSTFLOAT(0.005f), FAUSTFLOAT(0.6f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("dcw", &fHslider3, FAUSTFLOAT(0.32f), FAUSTFLOAT(0.05f), FAUSTFLOAT(0.5f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider4, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("release", &fHslider0, FAUSTFLOAT(0.25f), FAUSTFLOAT(0.02f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow4 = 1.0f / fSlow3;
		float fSlow5 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow6 = float(fHslider3);
		float fSlow7 = fConst4 * float(fHslider4);
		float fSlow8 = 0.78f * float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			iRec2[0] = (iRec2[1] + (iRec2[1] > 0)) * (fSlow0 <= fVec1[1]) + (fSlow0 > fVec1[1]);
			float fTemp0 = float(iRec2[0]);
			float fTemp1 = std::max<float>(0.0f, std::min<float>(fConst3 * fTemp0, fSlow5 * (fConst2 - fTemp0) + 1.0f));
			float fTemp2 = std::max<float>(0.04f, std::min<float>(0.96f, fSlow6 * (1.0f - fTemp1) + 0.1f * fTemp1));
			float fTemp3 = ((1 - iVec0[1]) ? 0.0f : fSlow7 + fRec3[1]);
			fRec3[0] = fTemp3 - std::floor(fTemp3);
			float fTemp4 = fSlow8 * std::cos(6.2831855f * ((fRec3[0] < fTemp2) ? 0.5f * (fRec3[0] / fTemp2) : 0.5f * ((fRec3[0] - fTemp2) / (1.0f - fTemp2) + 1.0f))) * std::max<float>(0.0f, std::min<float>(fSlow4 * fRec1[0], std::max<float>(fConst1 * (fSlow3 - fRec1[0]) + 1.0f, 0.6f)) * (1.0f - fSlow2 * float(iRec0[0])));
			output0[i0] = FAUSTFLOAT(fTemp4);
			output1[i0] = FAUSTFLOAT(fTemp4);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			iRec2[1] = iRec2[0];
			fRec3[1] = fRec3[0];
		}
	}

};

#endif
