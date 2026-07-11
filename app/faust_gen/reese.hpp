/* ------------------------------------------------------------
name: "reese"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Reese -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Reese_H__
#define  __Reese_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Reese
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

static float Reese_faustpower2_f(float value) {
	return value * value;
}

class Reese : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fConst1;
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec3[2];
	FAUSTFLOAT fHslider2;
	float fRec4[2];
	float fConst2;
	float fConst3;
	float fConst4;
	FAUSTFLOAT fHslider3;
	FAUSTFLOAT fHslider4;
	float fConst5;
	float fRec5[2];
	float fRec7[2];
	float fRec9[2];
	float fRec11[2];
	FAUSTFLOAT fHslider5;
	float fVec1[2];
	float fRec2[2];
	float fRec1[3];
	float fRec0[3];
	
 public:
	Reese() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Reese -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "reese.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonlp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonlp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonlp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "reese");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
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
		fConst1 = 3.1415927f / fConst0;
		fConst2 = std::max<float>(1.0f, 0.01f * fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = 0.15f / std::max<float>(1.0f, 0.2f * fConst0);
		fConst5 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(1.2e+03f);
		fHslider1 = FAUSTFLOAT(4.0f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider2 = FAUSTFLOAT(0.3f);
		fHslider3 = FAUSTFLOAT(0.015f);
		fHslider4 = FAUSTFLOAT(55.0f);
		fHslider5 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec3[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec4[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec5[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec7[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec9[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec11[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fVec1[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec2[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec1[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fRec0[l10] = 0.0f;
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
	
	virtual Reese* clone() {
		return new Reese();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("reese");
		ui_interface->addHorizontalSlider("cutoff", &fHslider0, FAUSTFLOAT(1.2e+03f), FAUSTFLOAT(5e+01f), FAUSTFLOAT(1.2e+04f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("detune", &fHslider3, FAUSTFLOAT(0.015f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.06f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider4, FAUSTFLOAT(55.0f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("release", &fHslider2, FAUSTFLOAT(0.3f), FAUSTFLOAT(0.02f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("res", &fHslider1, FAUSTFLOAT(4.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst1 * float(fHslider0));
		float fSlow1 = 2.0f * (1.0f - 1.0f / Reese_faustpower2_f(fSlow0));
		float fSlow2 = 1.0f / float(fHslider1);
		float fSlow3 = 1.0f / fSlow0;
		float fSlow4 = (fSlow3 - fSlow2) / fSlow0 + 1.0f;
		float fSlow5 = (fSlow2 + fSlow3) / fSlow0 + 1.0f;
		float fSlow6 = 1.0f / fSlow5;
		float fSlow7 = (fSlow3 + -1.0f) / fSlow0 + 1.0f;
		float fSlow8 = 1.0f / ((fSlow3 + 1.0f) / fSlow0 + 1.0f);
		float fSlow9 = 1.0f - fSlow3;
		float fSlow10 = float(fButton0);
		int iSlow11 = fSlow10 == 0.0f;
		float fSlow12 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow13 = float(fHslider3);
		float fSlow14 = float(fHslider4);
		float fSlow15 = std::max<float>(1.1920929e-07f, std::fabs(fSlow14 * (fSlow13 + 1.0f)));
		float fSlow16 = fConst5 * fSlow15;
		float fSlow17 = 1.0f - fConst0 / fSlow15;
		float fSlow18 = std::max<float>(1.1920929e-07f, std::fabs(fSlow14));
		float fSlow19 = fConst5 * fSlow18;
		float fSlow20 = 1.0f - fConst0 / fSlow18;
		float fSlow21 = std::max<float>(1.1920929e-07f, std::fabs(fSlow14 * (1.0f - fSlow13)));
		float fSlow22 = fConst5 * fSlow21;
		float fSlow23 = 1.0f - fConst0 / fSlow21;
		float fSlow24 = std::max<float>(1.1920929e-07f, std::fabs(fSlow14 * (2.0f * fSlow13 + 1.0f)));
		float fSlow25 = fConst5 * fSlow24;
		float fSlow26 = 1.0f - fConst0 / fSlow24;
		float fSlow27 = 0.5f * float(fHslider5);
		float fSlow28 = 1.0f / (fSlow3 + 1.0f);
		float fSlow29 = 0.53f / fSlow5;
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow10;
			iRec3[0] = iSlow11 * (iRec3[1] + 1);
			fRec4[0] = fSlow10 + fRec4[1] * float(fVec0[1] >= fSlow10);
			float fTemp0 = fSlow16 + fRec5[1] + -1.0f;
			int iTemp1 = fTemp0 < 0.0f;
			float fTemp2 = fSlow16 + fRec5[1];
			fRec5[0] = ((iTemp1) ? fTemp2 : fTemp0);
			float fRec6 = ((iTemp1) ? fTemp2 : fSlow16 + fRec5[1] + fSlow17 * fTemp0);
			float fTemp3 = fSlow19 + fRec7[1] + -1.0f;
			int iTemp4 = fTemp3 < 0.0f;
			float fTemp5 = fSlow19 + fRec7[1];
			fRec7[0] = ((iTemp4) ? fTemp5 : fTemp3);
			float fRec8 = ((iTemp4) ? fTemp5 : fSlow19 + fRec7[1] + fSlow20 * fTemp3);
			float fTemp6 = fSlow22 + fRec9[1] + -1.0f;
			int iTemp7 = fTemp6 < 0.0f;
			float fTemp8 = fSlow22 + fRec9[1];
			fRec9[0] = ((iTemp7) ? fTemp8 : fTemp6);
			float fRec10 = ((iTemp7) ? fTemp8 : fSlow22 + fRec9[1] + fSlow23 * fTemp6);
			float fTemp9 = fSlow25 + fRec11[1] + -1.0f;
			int iTemp10 = fTemp9 < 0.0f;
			float fTemp11 = fSlow25 + fRec11[1];
			fRec11[0] = ((iTemp10) ? fTemp11 : fTemp9);
			float fRec12 = ((iTemp10) ? fTemp11 : fSlow25 + fRec11[1] + fSlow26 * fTemp9);
			float fTemp12 = fSlow27 * (1.0f - (fRec12 + (fRec10 - (1.0f - (fRec8 + fRec6))))) * std::max<float>(0.0f, std::min<float>(fConst3 * fRec4[0], std::max<float>(fConst4 * (fConst2 - fRec4[0]) + 1.0f, 0.85f)) * (1.0f - fSlow12 * float(iRec3[0])));
			fVec1[0] = fTemp12;
			fRec2[0] = -(fSlow28 * (fTemp12 + fVec1[1] + fSlow9 * fRec2[1]));
			fRec1[0] = fRec2[0] - fSlow8 * (fSlow7 * fRec1[2] + fSlow1 * fRec1[1]);
			fRec0[0] = fSlow8 * (fRec1[2] + fRec1[0] + 2.0f * fRec1[1]) - fSlow6 * (fSlow4 * fRec0[2] + fSlow1 * fRec0[1]);
			float fTemp13 = fSlow29 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp13);
			output1[i0] = FAUSTFLOAT(fTemp13);
			fVec0[1] = fVec0[0];
			iRec3[1] = iRec3[0];
			fRec4[1] = fRec4[0];
			fRec5[1] = fRec5[0];
			fRec7[1] = fRec7[0];
			fRec9[1] = fRec9[0];
			fRec11[1] = fRec11[0];
			fVec1[1] = fVec1[0];
			fRec2[1] = fRec2[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
