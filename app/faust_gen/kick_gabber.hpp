/* ------------------------------------------------------------
name: "kick_gabber"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn KickGabber -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __KickGabber_H__
#define  __KickGabber_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS KickGabber
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

class KickGabberSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec3[2];
	
  public:
	
	int getNumInputsKickGabberSIG0() {
		return 0;
	}
	int getNumOutputsKickGabberSIG0() {
		return 1;
	}
	
	void instanceInitKickGabberSIG0(int sample_rate) {
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iVec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec3[l5] = 0;
		}
	}
	
	void fillKickGabberSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec3[0] = (iVec2[1] + iRec3[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec3[0]));
			iVec2[1] = iVec2[0];
			iRec3[1] = iRec3[0];
		}
	}

};

static KickGabberSIG0* newKickGabberSIG0() { return (KickGabberSIG0*)new KickGabberSIG0(); }
static void deleteKickGabberSIG0(KickGabberSIG0* dsp) { delete dsp; }

static float KickGabber_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0KickGabberSIG0[65536];

class KickGabber : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fRec1[2];
	float fConst2;
	float fConst3;
	FAUSTFLOAT fHslider0;
	float fConst4;
	float fConst6;
	float fConst8;
	float fConst10;
	float fConst11;
	int iRec5[2];
	float fConst12;
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	float fConst13;
	float fRec4[2];
	FAUSTFLOAT fHslider3;
	FAUSTFLOAT fHslider4;
	float fRec2[3];
	float fConst14;
	float fConst16;
	float fConst18;
	float fConst20;
	float fRec6[3];
	float fConst21;
	float fConst23;
	float fConst25;
	float fConst27;
	float fRec7[3];
	float fConst28;
	FAUSTFLOAT fHslider5;
	float fConst31;
	float fConst33;
	float fConst35;
	int iRec9[2];
	float fRec8[3];
	float fConst36;
	float fConst37;
	float fConst38;
	FAUSTFLOAT fHslider6;
	float fConst39;
	FAUSTFLOAT fHslider7;
	
 public:
	KickGabber() {}

	void metadata(Meta* m) { 
		m->declare("aanl.lib/name", "Faust Antialiased Nonlinearities");
		m->declare("aanl.lib/version", "1.3.0");
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn KickGabber -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "kick_gabber.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "kick_gabber");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
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
		KickGabberSIG0* sig0 = newKickGabberSIG0();
		sig0->instanceInitKickGabberSIG0(sample_rate);
		sig0->fillKickGabberSIG0(65536, ftbl0KickGabberSIG0);
		deleteKickGabberSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / std::max<float>(1.0f, 0.05f * fConst0);
		fConst2 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = 0.8f * fConst0;
		float fConst5 = std::tan(16336.282f / fConst0);
		fConst6 = 2.0f * (1.0f - 1.0f / KickGabber_faustpower2_f(fConst5));
		float fConst7 = 1.0f / fConst5;
		fConst8 = (fConst7 + -0.2f) / fConst5 + 1.0f;
		float fConst9 = (fConst7 + 0.2f) / fConst5 + 1.0f;
		fConst10 = 1.0f / fConst9;
		fConst11 = 1.0f / std::max<float>(1.0f, 0.07f * fConst0);
		fConst12 = 1.0f / std::max<float>(1.0f, 0.035f * fConst0);
		fConst13 = 1.0f / fConst0;
		fConst14 = 0.8f / (fConst5 * fConst9);
		float fConst15 = std::tan(8168.141f / fConst0);
		fConst16 = 2.0f * (1.0f - 1.0f / KickGabber_faustpower2_f(fConst15));
		float fConst17 = 1.0f / fConst15;
		fConst18 = (fConst17 + -0.25f) / fConst15 + 1.0f;
		float fConst19 = (fConst17 + 0.25f) / fConst15 + 1.0f;
		fConst20 = 1.0f / fConst19;
		fConst21 = 0.9f / (fConst15 * fConst19);
		float fConst22 = std::tan(3769.9111f / fConst0);
		fConst23 = 2.0f * (1.0f - 1.0f / KickGabber_faustpower2_f(fConst22));
		float fConst24 = 1.0f / fConst22;
		fConst25 = (fConst24 + -0.33333334f) / fConst22 + 1.0f;
		float fConst26 = (fConst24 + 0.33333334f) / fConst22 + 1.0f;
		fConst27 = 1.0f / fConst26;
		fConst28 = 1.0f / (fConst22 * fConst26);
		float fConst29 = std::tan(5654.8667f / fConst0);
		float fConst30 = KickGabber_faustpower2_f(fConst29);
		fConst31 = 2.0f * (1.0f - 1.0f / fConst30);
		float fConst32 = 1.0f / fConst29;
		fConst33 = (fConst32 + -1.4142135f) / fConst29 + 1.0f;
		float fConst34 = (fConst32 + 1.4142135f) / fConst29 + 1.0f;
		fConst35 = 1.0f / fConst34;
		fConst36 = std::max<float>(1.0f, 0.0004f * fConst0);
		fConst37 = 1.0f / fConst36;
		fConst38 = 1.0f / std::max<float>(1.0f, 0.01f * fConst0);
		fConst39 = 1.0f / (fConst30 * fConst34);
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.34f);
		fHslider1 = FAUSTFLOAT(3.6f);
		fHslider2 = FAUSTFLOAT(55.0f);
		fHslider3 = FAUSTFLOAT(7.0f);
		fHslider4 = FAUSTFLOAT(0.65f);
		fHslider5 = FAUSTFLOAT(0.5f);
		fHslider6 = FAUSTFLOAT(0.8f);
		fHslider7 = FAUSTFLOAT(0.9f);
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
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec5[l6] = 0;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec4[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 3; l8 = l8 + 1) {
			fRec2[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec6[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fRec7[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			iRec9[l11] = 0;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec8[l12] = 0.0f;
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
	
	virtual KickGabber* clone() {
		return new KickGabber();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("kick_gabber");
		ui_interface->addHorizontalSlider("crunch", &fHslider4, FAUSTFLOAT(0.65f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(0.34f), FAUSTFLOAT(0.05f), FAUSTFLOAT(1.2f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("drive", &fHslider3, FAUSTFLOAT(7.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(14.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("drop", &fHslider1, FAUSTFLOAT(3.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(55.0f), FAUSTFLOAT(25.0f), FAUSTFLOAT(2e+02f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("gain", &fHslider7, FAUSTFLOAT(0.9f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("punch", &fHslider6, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("screech", &fHslider5, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = float(fHslider0);
		float fSlow3 = 1.0f / std::max<float>(1.0f, fConst4 * fSlow2);
		float fSlow4 = 1.0f / std::max<float>(1.0f, fConst0 * fSlow2);
		float fSlow5 = float(fHslider1);
		float fSlow6 = fConst13 * float(fHslider2);
		float fSlow7 = float(fHslider3);
		float fSlow8 = float(fHslider4);
		float fSlow9 = 1.0f - fSlow8;
		float fSlow10 = 4.0f * float(fHslider5);
		float fSlow11 = fConst39 * float(fHslider6);
		float fSlow12 = float(fHslider7);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			float fTemp0 = float(iRec0[0]);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			float fTemp1 = fConst3 * fRec1[0];
			float fTemp2 = fConst2 - fRec1[0];
			iRec5[0] = (fSlow0 > fVec1[1]) + (fSlow0 <= fVec1[1]) * (iRec5[1] + (iRec5[1] > 0));
			float fTemp3 = float(iRec5[0]);
			float fTemp4 = ((1 - iVec0[1]) ? 0.0f : fRec4[1] + fSlow6 * (fSlow5 * std::max<float>(0.0f, std::min<float>(fConst3 * fTemp3, fConst12 * (fConst2 - fTemp3) + 1.0f)) + 1.0f));
			fRec4[0] = fTemp4 - std::floor(fTemp4);
			float fTemp5 = tanhf(fSlow7 * ftbl0KickGabberSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec4[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fTemp1, std::max<float>(fSlow4 * fTemp2 + 1.0f, 0.0f)) * (1.0f - fConst11 * fTemp0)));
			float fTemp6 = fSlow9 * fTemp5 + fSlow8 * std::max<float>(-0.8f, std::min<float>(0.8f, 1.8f * fTemp5));
			fRec2[0] = fTemp6 - fConst10 * (fConst8 * fRec2[2] + fConst6 * fRec2[1]);
			fRec6[0] = fTemp6 - fConst20 * (fConst18 * fRec6[2] + fConst16 * fRec6[1]);
			fRec7[0] = fTemp6 - fConst27 * (fConst25 * fRec7[2] + fConst23 * fRec7[1]);
			iRec9[0] = 1103515245 * iRec9[1] + 12345;
			fRec8[0] = 4.656613e-10f * float(iRec9[0]) - fConst35 * (fConst33 * fRec8[2] + fConst31 * fRec8[1]);
			float fTemp7 = fSlow12 * tanhf(0.5f * (fSlow11 * std::max<float>(0.0f, std::min<float>(fConst37 * fTemp3, fConst38 * (fConst36 - fTemp3) + 1.0f)) * (fRec8[0] + fRec8[2] - 2.0f * fRec8[1]) + 0.85f * fTemp6 + fSlow10 * (fConst28 * (fRec7[0] - fRec7[2]) + fConst21 * (fRec6[0] - fRec6[2]) + fConst14 * (fRec2[0] - fRec2[2])) * std::max<float>(0.0f, std::min<float>(fTemp1, std::max<float>(fSlow3 * fTemp2 + 1.0f, 0.0f)) * (1.0f - fConst1 * fTemp0))));
			output0[i0] = FAUSTFLOAT(fTemp7);
			output1[i0] = FAUSTFLOAT(fTemp7);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			iRec5[1] = iRec5[0];
			fRec4[1] = fRec4[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec6[2] = fRec6[1];
			fRec6[1] = fRec6[0];
			fRec7[2] = fRec7[1];
			fRec7[1] = fRec7[0];
			iRec9[1] = iRec9[0];
			fRec8[2] = fRec8[1];
			fRec8[1] = fRec8[0];
		}
	}

};

#endif
